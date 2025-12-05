# utils/sqlite_store.py
import os
import json
import sqlite3

class SQLiteStore:
    def __init__(self, db_path="memory.db", namespace="default"):
        self.db_path = db_path
        self.namespace = namespace
        # Create directory if db_path has a folder
        os.makedirs(os.path.dirname(db_path), exist_ok=True) if "/" in db_path else None
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    namespace TEXT,
                    key TEXT,
                    value TEXT,
                    PRIMARY KEY(namespace, key)
                )
            """)

    def set(self, key, value):
        value_json = json.dumps(value)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO memory(namespace, key, value) VALUES (?, ?, ?)",
                (self.namespace, key, value_json)
            )

    def get(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT value FROM memory WHERE namespace=? AND key=?",
                (self.namespace, key)
            )
            row = cur.fetchone()
            return json.loads(row[0]) if row else default

    def all(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT key, value FROM memory WHERE namespace=?",
                (self.namespace,)
            )
            return {k: json.loads(v) for k, v in cur.fetchall()}
