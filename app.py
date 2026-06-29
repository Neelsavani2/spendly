import os

from flask import Flask, render_template, request, session, redirect, url_for
from database.db import get_db, init_db, seed_db, create_user, find_user_by_email, verify_user, find_user_by_id

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

    user = {
        "name":         "Priya Mehta",
        "email":        "priya.mehta@gmail.com",
        "member_since": "March 2024",
    }
    stats = {
        "total_spent":  "₹24,850",
        "this_month":   "₹6,320",
        "transactions": 47,
        "top_category": "Food",
    }
    transactions = [
        {"date": "28 Jun 2026", "description": "Grocery run at D-Mart",  "category": "Food",          "amount": "₹1,240"},
        {"date": "26 Jun 2026", "description": "BESCOM electricity bill", "category": "Bills",         "amount": "₹2,150"},
        {"date": "24 Jun 2026", "description": "Ola cab to office",       "category": "Transport",     "amount": "₹380"},
        {"date": "22 Jun 2026", "description": "Apollo pharmacy",         "category": "Health",        "amount": "₹540"},
        {"date": "20 Jun 2026", "description": "Netflix subscription",    "category": "Entertainment", "amount": "₹649"},
    ]
    categories = [
        {"name": "Food",          "amount": "₹8,420", "percent": 34},
        {"name": "Bills",         "amount": "₹6,150", "percent": 25},
        {"name": "Transport",     "amount": "₹3,720", "percent": 15},
        {"name": "Health",        "amount": "₹3,215", "percent": 13},
        {"name": "Entertainment", "amount": "₹3,345", "percent": 13},
    ]
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
