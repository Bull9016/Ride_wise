import sqlite3
import os
import uuid
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, db_path: str = "data/chat_state.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    sender_role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_summaries (
                    session_id TEXT PRIMARY KEY,
                    summary_text TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()
            
    def ensure_session(self, session_id: str, customer_id: Optional[str] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO sessions (session_id, customer_id) VALUES (?, ?)", (session_id, customer_id))
            conn.commit()

    def add_message(self, session_id: str, role: str, content: str):
        msg_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (message_id, session_id, sender_role, content) VALUES (?, ?, ?, ?)",
                           (msg_id, session_id, role, content))
            conn.commit()

    def get_recent_messages(self, session_id: str, limit: int = 6) -> List[Dict[str, str]]:
        # Limit 6 means 3 user-assistant pairs
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sender_role, content FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?", (session_id, limit))
            rows = cursor.fetchall()
            return [{"role": row["sender_role"], "content": row["content"]} for row in reversed(rows)]
            
    def get_summary(self, session_id: str) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT summary_text FROM memory_summaries WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return row["summary_text"] if row else ""
            
    def set_summary(self, session_id: str, summary_text: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO memory_summaries (session_id, summary_text) VALUES (?, ?)", (session_id, summary_text))
            conn.commit()
