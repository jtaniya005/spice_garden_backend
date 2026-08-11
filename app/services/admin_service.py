import os
import sqlite3
import uuid
from datetime import datetime
from app.db.local_db import get_connection, row_to_dict

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "taniya")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "2005")


def create_admin_session(username: str, password: str) -> str:
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise ValueError("Invalid admin credentials")

    token = uuid.uuid4().hex
    created_at = datetime.now().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO admin_sessions (token, created_at) VALUES (?, ?)",
        (token, created_at),
    )
    conn.commit()
    conn.close()
    return token


def validate_admin_token(token: str) -> bool:
    if not token:
        return False
    conn = get_connection()
    row = conn.execute("SELECT * FROM admin_sessions WHERE token = ?", (token,)).fetchone()
    conn.close()
    return bool(row)


def revoke_admin_session(token: str) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM admin_sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()
