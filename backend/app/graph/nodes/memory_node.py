import os
import json
import sqlite3
from typing import Dict, Any, List
from app.graph.state import GraphState
from app.core.config import settings
from app.core.logger import logger

class MemoryStoreManager:
    def __init__(self, db_path: str = settings.SQLITE_MEMORY_DB):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    session_id TEXT PRIMARY KEY,
                    messages_json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT messages_json FROM conversation_memory WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except Exception:
                    return []
            return []

    def save_turn(self, session_id: str, user_msg: str, assistant_msg: str):
        existing = self.get_messages(session_id)
        existing.append({"role": "user", "content": user_msg})
        existing.append({"role": "assistant", "content": assistant_msg})
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_memory (session_id, messages_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    messages_json = excluded.messages_json,
                    updated_at = CURRENT_TIMESTAMP
            """, (session_id, json.dumps(existing)))

    def clear_memory(self, session_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conversation_memory WHERE session_id = ?", (session_id,))

memory_store = MemoryStoreManager()

def memory_node(state: GraphState) -> Dict[str, Any]:
    session_id = state.get("session_id", "default")
    user_query = state.get("raw_query", "")
    final_resp = state.get("final_response", "")

    logger.info(f"Executing memory_node for session '{session_id}'")
    if user_query and final_resp:
        memory_store.save_turn(session_id, user_query, final_resp)

    updated_messages = memory_store.get_messages(session_id)
    return {"messages": updated_messages}
