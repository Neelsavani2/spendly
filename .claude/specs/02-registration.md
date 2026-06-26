# Spec: Registration

## Overview
Handles the `POST /register` form submission — the first point where a visitor becomes a persisted user. It validates the submitted name, email, and password, creates a hashed record in the `users` table, writes the user's id into a Flask session, and redirects to the dashboard. This step closes the loop on the sign-up flow started in Step 1 (landing page CTA → register page).

## Depends on
- Step 1 (landing page) — `GET /register` route and `register.html` template already exist

## Routes
- `POST /register` — processes the sign-up form — public

## Database changes
No new tables or columns. Two new helper functions added to `database/db.py`:

- `find_user_by_email(email)` — returns a `sqlite3.Row` or `None`
- `create_user(name, email, password)` — hashes password with werkzeug, inserts row, returns the new row

## Templates
- **Modify:** `templates/register.html` — add `value="{{ name or '' }}"` and `value="{{ email or '' }}"` to the name and email inputs so fields are sticky on validation errors

## Files to change
- `database/db.py` — add `find_user_by_email()` and `create_user()`
- `app.py` — convert `GET /register` to `GET|POST`, add POST logic, import new helpers and `session`/`redirect`/`request`, set `app.secret_key`
- `templates/register.html` — sticky field values

## Files to create
- `tests/test_registration.py` — pytest test suite

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never f-strings in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — never inline in route functions
- On validation failure: re-render `register.html` with `error=` variable, never redirect
- `app.secret_key` must use `os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")`

## Definition of done
- [ ] `POST /register` with valid data creates a user row in `users` and sets `session["user_id"]`
- [ ] Submitting a duplicate email shows an error message and does not insert a second row
- [ ] Submitting a password shorter than 8 characters shows an error message
- [ ] Submitting a blank name shows an error message
- [ ] On any error, the name and email fields are pre-filled with the submitted values
- [ ] The `password_hash` column does not contain the raw password string
- [ ] All 8 pytest tests in `tests/test_registration.py` pass
