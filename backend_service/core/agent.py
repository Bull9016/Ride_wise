import json
import logging
from typing import Dict, Any, List

from core.llm import LLMClient
from core.security import AccessControlManager
from services.database import DatabaseService
from services.knowledge import KnowledgeBaseService

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, db_service: DatabaseService, kb_service: KnowledgeBaseService):
        self.llm_client = LLMClient()
        self.db_service = db_service
        self.kb_service = kb_service
        
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

    def chat(self, user_message: str, role: str, history: List[Dict[str, str]] = None, mobile_number: str = None, customer_id: str = None) -> str:
        """
        Main entry point for handling a user's message.
        """
        resolved_customer_id = customer_id
        history = history or []
        
        if role.lower() == "customer":
            if mobile_number and not customer_id:
                resolved_customer_id = self.db_service.get_customer_id_by_phone(mobile_number)
                if not resolved_customer_id:
                    return "Sorry, I could not find a customer account associated with that mobile number."
            elif not resolved_customer_id:
                return "Authentication error: Customer ID or Mobile Number required."
                
        system_prompt = f"""
You are RideWise Assist, an AI assistant for a two-wheeler and EV rental company.
You are assisting a {role.upper()}.
{f"The customer's ID is: {resolved_customer_id}. You MUST ALWAYS include WHERE customer_id = '{resolved_customer_id}' in ANY database queries." if role.lower() == 'customer' else "You have full support agent access."}

You have two tools available:
1. query_operational_database: Use this to fetch live structured data.
2. query_rental_policies: Use this to check rules and penalties.

Use the tools to gather necessary context before answering.
Answer factually. Do not hallucinate. If the data is not in the DB or policies, say "I don't know".

{self._get_schema_prompt()}
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})
        
        MAX_ITERATIONS = 5
        for _ in range(MAX_ITERATIONS):
            response_msg = self.llm_client.generate_response(messages, tools=self.tools)
            messages.append(response_msg) # Append the assistant's message (which might contain tool_calls)
            
            if not response_msg.tool_calls:
                return response_msg.content # No more tools, this is the final answer
                
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
                
        return "I'm sorry, I had to stop because it took too many steps to find the answer."
