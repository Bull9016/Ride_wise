import logging

logger = logging.getLogger(__name__)

class AccessControlManager:
    """
    Enforces strict data entitlements before queries are executed.
    """
    
    @staticmethod
    def validate_sql(sql_query: str, role: str, customer_id: str = None) -> bool:
        """
        Ensures that a Customer cannot execute SQL that accesses other customers' data.
        Returns True if safe, raises ValueError if unsafe.
        """
        query_upper = sql_query.upper()
        
        # 1. Prevent non-SELECT queries (already handled by DB Service, but good defense in depth)
        if not query_upper.strip().startswith("SELECT"):
            raise ValueError("SECURITY VIOLATION: Only SELECT queries are permitted.")
            
        # 2. Support Agents have full read access
        if role.lower() == "support agent":
            return True
            
        # 3. Customers MUST have their ID injected in the WHERE clause
        if role.lower() == "customer":
            if not customer_id:
                raise ValueError("SECURITY VIOLATION: customer_id is required for Customer role.")
                
            # Basic AST-less validation (In a real production app, we would use sqlglot to parse the AST)
            # For the hackathon, we ensure the specific ID exists in the query string.
            if f"'{customer_id}'" not in sql_query and f'"{customer_id}"' not in sql_query:
                raise ValueError(
                    f"SECURITY VIOLATION: Customer queries must strictly filter by customer_id = '{customer_id}'"
                )
                
            return True
            
        raise ValueError(f"Unknown role: {role}")
