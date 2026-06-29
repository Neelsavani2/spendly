import os
from datetime import datetime

from flask import Flask, render_template, request, session, redirect, url_for
from database.db import (
    get_db, init_db, seed_db,
    create_user, find_user_by_email, verify_user, find_user_by_id,
    get_profile_stats, get_recent_transactions, get_category_breakdown,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("register.html")

    name     = request.form.get("name",     "").strip()
    email    = request.form.get("email",    "").strip().lower()
    password = request.form.get("password", "").strip()

    if not name:
        return render_template("register.html", error="Name is required.", email=email)
    if not email:
        return render_template("register.html", error="Email is required.", name=name)
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.", name=name, email=email)
    if find_user_by_email(email):
        return render_template("register.html", error="An account with that email already exists.", name=name, email=email)

    user = create_user(name, email, password)
    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email",    "").strip().lower()
    password = request.form.get("password", "").strip()

    if not email:
        return render_template("login.html", error="Email is required.")
    if not password:
        return render_template("login.html", error="Password is required.", email=email)

    user = verify_user(email, password)
    if user is None:
        return render_template("login.html", error="Invalid email or password.", email=email)

    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/dashboard")
def dashboard():
    user = find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # --- SECTION: user + stats (Subagent 2) ---
    raw_user = find_user_by_id(user_id)
    dt = datetime.strptime(raw_user["created_at"], "%Y-%m-%d %H:%M:%S")
    user = {
        "name":         raw_user["name"],
        "email":        raw_user["email"],
        "member_since": dt.strftime("%B %Y"),
    }
    stats = get_profile_stats(user_id)
    # --- END SECTION: user + stats ---

    # --- SECTION: transactions (Subagent 1) ---
    transactions = get_recent_transactions(user_id)
    # --- END SECTION: transactions ---

    # --- SECTION: categories (Subagent 3) ---
    categories = get_category_breakdown(user_id)
    # --- END SECTION: categories ---

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
