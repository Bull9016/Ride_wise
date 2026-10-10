import sqlite3
import logging
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service to handle read-only interactions with the SQLite operational database.
    Strictly follows OOP and ensures data integrity.
    """
    
    def __init__(self, db_path: str = "data/ridewise.db"):
        self.db_path = db_path
        # Use URI read-only mode to completely prevent modifications
        self.db_uri = f"file:{os.path.abspath(self.db_path)}?mode=ro"

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes a read-only connection to the database."""
        try:
            conn = sqlite3.connect(self.db_uri, uri=True)
            conn.row_factory = sqlite3.Row  # Returns rows as dictionaries
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a SELECT query and returns the results as a list of dictionaries.
        """
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are permitted.")
            
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"SQL execution error: {e} | Query: {query}")
            raise ValueError(f"SQL Error: {str(e)}")

    def get_customer_id_by_phone(self, phone: str) -> Optional[str]:
        """
        Looks up a customer_id using their 10-digit mobile number.
        """
        query = f"SELECT customer_id FROM customers WHERE phone = '{phone}' LIMIT 1;"
        results = self.execute_query(query)
        if results:
            return results[0].get("customer_id")
        return None

    def verify_credentials(self, customer_id: str, phone: str) -> bool:
        """
        Strictly verifies that the provided customer_id matches the provided phone number.
        """
        if not customer_id or not phone:
            return False
        customer_id = customer_id.strip()
        phone = phone.strip()
        query = f"SELECT 1 FROM customers WHERE customer_id = '{customer_id}' AND phone = '{phone}' LIMIT 1;"
        try:
            results = self.execute_query(query)
            return len(results) > 0
        except Exception as e:
            logger.error(f"Error verifying credentials: {e}")
            return False
