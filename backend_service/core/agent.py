import json
import logging
from typing import Dict, Any, List

from core.llm import LLMClient
from core.security import AccessControlManager
from services.database import DatabaseService
from services.knowledge import KnowledgeBaseService

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, db_service: DatabaseService, kb_service: KnowledgeBaseService, memory_service):
        self.llm_client = LLMClient()
        self.db_service = db_service
        self.kb_service = kb_service
        self.memory_service = memory_service
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "query_operational_database",
                    "description": "Queries the operational SQLite database to fetch structured data like bookings, payments, and vehicles. Returns raw SQL results. IMPORTANT: Only use SELECT statements.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql_query": {
                                "type": "string",
                                "description": "The exact SQL query to execute."
                            }
                        },
                        "required": ["sql_query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_rental_policies",
                    "description": "Searches the unstructured policy documents (PDFs) for rules regarding rentals, penalties, cancellation, EVs, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "The search term or question to query the knowledge base."
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            }
        ]
        
    def _get_schema_prompt(self) -> str:
        # A simplified schema dump for the LLM to understand the DB
        return """
Database Schema:
1. customers (customer_id, full_name, phone, email, city, date_of_birth, driving_license_no, kyc_status, customer_tier, created_at)
2. vehicles (vehicle_id, registration_no, vehicle_type, model, hub_name, hourly_rate, daily_rate, battery_capacity_kwh, status, commissioned_on)
3. bookings (booking_id, customer_id, vehicle_id, booked_at, scheduled_start, scheduled_end, actual_return_at, cancelled_at, booking_status, return_battery_pct)
4. payments (payment_id, booking_id, payment_type, amount, gst_amount, payment_method, payment_status, transaction_ref, paid_at, remarks)
5. damage_reports (report_id, booking_id, vehicle_id, reported_by, damage_category, severity, description, assessed_cost, claim_status, reported_at)
"""

    def chat(self, user_message: str, role: str, session_id: str, mobile_number: str = None, customer_id: str = None) -> str:
        """
        Main entry point for handling a user's message.
        """
        resolved_customer_id = customer_id
        
        customer_context = ""
        if role.lower() == "customer":
            if mobile_number and not customer_id:
                resolved_customer_id = self.db_service.get_customer_id_by_phone(mobile_number)
                if not resolved_customer_id:
                    return "Sorry, I could not find a customer account associated with that mobile number."
            elif not resolved_customer_id:
                return "Authentication error: Customer ID or Mobile Number required."
                
            try:
                cust_data = self.db_service.execute_query(f"SELECT full_name FROM customers WHERE customer_id = '{resolved_customer_id}'")
                if cust_data:
                    c = cust_data[0]
                    customer_context = f"The customer's name is {c.get('full_name')}. Greet them warmly by name in your first response."
            except Exception as e:
                logger.error(f"Error fetching customer context: {e}")
                
        # Register the session in persistent memory
        self.memory_service.ensure_session(session_id, resolved_customer_id)
        
        role_specific_instructions = ""
        if role.lower() == "customer":
            role_specific_instructions = f"""You are assisting a CUSTOMER.
{customer_context}
The customer's ID is: {resolved_customer_id}. You MUST ALWAYS include WHERE customer_id = '{resolved_customer_id}' in ANY database queries. You must never query data for any other customer."""
        else:
            role_specific_instructions = """You are an internal tool assisting a human RideWise SUPPORT AGENT.
You have access to query the operational database.
CRITICAL SECURITY RULE: You MUST NEVER provide a customer's personal data or booking data unless the Support Agent provides BOTH the Customer ID AND the Customer's registered Phone Number in the chat.
If the Support Agent asks for data but only provides a Customer ID, you must refuse and ask for the Phone Number to verify.
If the user asks for their *own* personal data (e.g. "my rides", "my bookings"), assume they are a customer who accidentally entered the Support Agent workspace. You must reply: "You are currently in the Support Agent workspace. To access your personal data, please log in via the Customer Login Portal: [http://localhost:3000](http://localhost:3000)"
Do not treat the Support Agent as a customer (they do not rent vehicles)."""

        system_prompt = f"""
You are RideWise Assist, an AI assistant for a two-wheeler and EV rental company.
{role_specific_instructions}

You have two tools available:
1. query_operational_database: Use this to fetch live structured data.
2. query_rental_policies: Use this to check rules and penalties.

Use the tools to gather necessary context before answering.
CRITICAL RULES:
1. NEVER offer to check or mention battery levels for non-electric vehicles (BIKE or SCOOTER). Battery percentage is ONLY applicable for EV_SCOOTER and EV_BIKE.
2. If explicitly asked about the battery level of a petrol vehicle, state that it is a petrol vehicle and does not have a battery level.
3. Answer factually based ONLY on tool outputs. Do not hallucinate or assume. If the data is missing, state that you don't have that information.
4. FORMATTING: Whenever presenting data from the database (like lists of bookings, payments, vehicles, etc.), you MUST format it as a proper Markdown table using pipe `|` delimiters and `---` header separators. NEVER use raw tabs or spaces to align columns.
5. READ-ONLY RESTRICTION: You CANNOT modify, cancel, update, or delete any data. If the user asks you to make changes (like cancelling a booking), politely decline and state that you are a read-only informational assistant.

{self._get_schema_prompt()}
"""
        
        # Build messages from sliding window memory (limit=6 gives 3 pairs)
        recent_history = self.memory_service.get_recent_messages(session_id, limit=6)
        messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})
        
        MAX_ITERATIONS = 5
        final_answer = "I'm sorry, I had to stop because it took too many steps to find the answer."
        
        for _ in range(MAX_ITERATIONS):
            response_msg = self.llm_client.generate_response(messages, tools=self.tools)
            messages.append(response_msg) # Append the assistant's message (which might contain tool_calls)
            
            if not response_msg.tool_calls:
                final_answer = response_msg.content # No more tools, this is the final answer
                break
                
            for tool_call in response_msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                tool_result_str = ""
                try:
                    if tool_name == "query_operational_database":
                        sql = tool_args.get("sql_query")
                        # Validate SQL for security
                        AccessControlManager.validate_sql(sql, role, resolved_customer_id)
                        # Execute
                        results = self.db_service.execute_query(sql)
                        tool_result_str = json.dumps(results)
                        
                    elif tool_name == "query_rental_policies":
                        sq = tool_args.get("search_query")
                        tool_result_str = self.kb_service.search_policies(sq)
                        
                    else:
                        tool_result_str = f"Error: Unknown tool {tool_name}"
                        
                except Exception as e:
                    tool_result_str = f"Error executing tool: {str(e)}. Please correct your query and try again."
                    
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": tool_result_str
                })
        
        # Save the new exchange to persistent memory
        self.memory_service.add_message(session_id, "user", user_message)
        self.memory_service.add_message(session_id, "assistant", final_answer)
        
        return final_answer
