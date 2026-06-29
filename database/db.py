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
    conn = get_db()
    rows = conn.execute(
        "SELECT date, description, category, amount FROM expenses "
        "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        dt = datetime.strptime(r["date"], "%Y-%m-%d")
        result.append({
            "date": f"{dt.day} {dt.strftime('%b %Y')}",
            "description": r["description"] or "",
            "category": r["category"],
            "amount": f"₹{r['amount']:,.0f}",
        })
    return result
# --- END SECTION: transactions helper ---


# --- SECTION: stats helper (Subagent 2) ---
def get_profile_stats(user_id):
    conn = get_db()
    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]
    this_month = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses "
        "WHERE user_id = ? AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')",
        (user_id,)
    ).fetchone()[0]
    count = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]
    top_row = conn.execute(
        "SELECT category FROM expenses WHERE user_id = ? "
        "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    conn.close()
    return {
        "total_spent":  f"₹{total:,.0f}",
        "this_month":   f"₹{this_month:,.0f}",
        "transactions": count,
        "top_category": top_row["category"] if top_row else "—",
    }
# --- END SECTION: stats helper ---


# --- SECTION: categories helper (Subagent 3) ---
def get_category_breakdown(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    grand_total = sum(r["total"] for r in rows)
    result = []
    for r in rows:
        pct = round(r["total"] / grand_total * 100) if grand_total else 0
        result.append({
            "name":    r["category"],
            "amount":  f"₹{r['total']:,.0f}",
            "percent": pct,
        })
    return result
# --- END SECTION: categories helper ---
