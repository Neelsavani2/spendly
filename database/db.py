import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()

    row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] > 0:
        conn.close()
        return

    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123"))
    )

    expenses = [
        (1, 45.50,  "Food",          "2026-06-02", "Grocery run"),
        (1, 120.00, "Bills",         "2026-06-04", "Electricity bill"),
        (1, 35.00,  "Transport",     "2026-06-06", "Monthly bus pass top-up"),
        (1, 80.00,  "Health",        "2026-06-08", "Doctor consultation"),
        (1, 14.99,  "Entertainment", "2026-06-10", "Streaming subscription"),
        (1, 65.00,  "Shopping",      "2026-06-13", "New shoes"),
        (1, 55.75,  "Food",          "2026-06-15", "Restaurant dinner"),
        (1, 22.00,  "Other",         "2026-06-18", "Stationery and supplies"),
    ]

    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )

    conn.commit()
    conn.close()


def find_user_by_email(email):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return user


def find_user_by_id(user_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return user


def verify_user(email, password):
    user = find_user_by_email(email)
    if user is None:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def create_user(name, email, password):
    password_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    conn.commit()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return user


# --- SECTION: transactions helper (Subagent 1) ---
def get_recent_transactions(user_id, limit=5):
    pass  # TODO: implement
# --- END SECTION: transactions helper ---


# --- SECTION: stats helper (Subagent 2) ---
def get_profile_stats(user_id):
    pass  # TODO: implement
# --- END SECTION: stats helper ---


# --- SECTION: categories helper (Subagent 3) ---
def get_category_breakdown(user_id):
    pass  # TODO: implement
# --- END SECTION: categories helper ---
