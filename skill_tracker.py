"""backend/skill_tracker.py
Simple SQLite‑based skill exposure tracking.
"""
import os
import sqlite3
from typing import Tuple, List

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/users.db"))

def _ensure_db():
    """Create the users table if it does not exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skill TEXT,
            exposure INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()

# Ensure DB/table exist on import
_ensure_db()

def get_or_create_user(name: str) -> Tuple[int, str]:
    """Return (user_id, name). Create a row if not present."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        cur.execute("INSERT INTO users (name) VALUES (?)", (name,))
        user_id = cur.lastrowid
        conn.commit()
    conn.close()
    return user_id, name

def update_skill(user_id: int, skill_category: str) -> None:
    """Increment exposure for the given skill category for the user.
    If the user already has a row for that skill, increment exposure; otherwise insert.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT exposure FROM users WHERE id = ? AND skill = ?",
        (user_id, skill_category),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE users SET exposure = exposure + 1 WHERE id = ? AND skill = ?",
            (user_id, skill_category),
        )
    else:
        cur.execute(
            "INSERT INTO users (id, name, skill, exposure) VALUES (?,?,?,1)",
            (user_id, get_user_name(user_id), skill_category),
        )
    conn.commit()
    conn.close()

def get_user_name(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""

def get_skill_profile(user_id: int) -> List[Tuple[str, int]]:
    """Return a list of (skill, exposure) for the user."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT skill, exposure FROM users WHERE id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
