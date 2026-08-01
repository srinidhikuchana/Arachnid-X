"""
Minimal persistent memory. For V1 we only remember the user's name across
sessions, stored in a local SQLite file. Easy to extend later.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "webwarden.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            user_name TEXT
        )
    """)
    conn.commit()
    return conn


def get_user_name() -> str | None:
    conn = _get_conn()
    row = conn.execute("SELECT user_name FROM user_profile WHERE id = 1").fetchone()
    conn.close()
    return row[0] if row else None


def set_user_name(name: str) -> None:
    conn = _get_conn()
    conn.execute("""
        INSERT INTO user_profile (id, user_name) VALUES (1, ?)
        ON CONFLICT(id) DO UPDATE SET user_name = excluded.user_name
    """, (name,))
    conn.commit()
    conn.close()
