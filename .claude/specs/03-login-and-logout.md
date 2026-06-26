# Spec: Login and Logout

## Overview
Wires up the two remaining auth endpoints so a returning user can sign in and sign out. `POST /login` validates the submitted email and password against the stored hash, writes `session["user_id"]`, and redirects to the dashboard. `GET /logout` clears the session and redirects to the landing page. Together they complete the full auth loop: register → login → logout.

## Depends on
- Step 2 (Registration) — `find_user_by_email()` DB helper, `session["user_id"]` convention, and `app.secret_key` must already exist.

## Routes
- `POST /login` — validates credentials, starts session — public
- `GET /logout` — clears session, redirects to landing — public (safe to call when not logged in)

## Database changes
No new tables or columns. One new helper function added to `database/db.py`:

- `verify_user(email, password)` — calls `find_user_by_email()`, then `check_password_hash()` against the stored hash; returns the user row on success, `None` on any failure. Keeps werkzeug and all auth logic out of the route.

Also: add `check_password_hash` to the existing werkzeug import in `database/db.py`.

## Templates
- **Modify:** `templates/login.html`
  - Fix hardcoded `action="/login"` → `action="{{ url_for('login') }}"`
  - Make email input sticky: add `value="{{ email or '' }}"`
  - Password field must NOT be sticky

## Files to change
- `database/db.py` — add `check_password_hash` to werkzeug import; add `verify_user()`
- `app.py` — expand `GET /login` to `GET|POST`; implement `GET /logout`; import `verify_user`
- `templates/login.html` — fix action URL, sticky email
- `CLAUDE.md` — update route table to mark `/login` and `/logout` as implemented

## Files to create
- `tests/test_login_logout.py` — pytest test suite

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never f-strings in SQL
- Passwords checked with `werkzeug.security.check_password_hash` — never compare plain text
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — `verify_user()` must live there, not in the route
- On login failure: always return the same error message regardless of whether the email exists or the password is wrong — never reveal which field failed
- On validation failure: re-render `login.html` with `error=` and `email=`, never redirect
- `GET /logout` must work even when no session exists — do not abort or raise

## Definition of done
- [ ] `POST /login` with correct credentials sets `session["user_id"]` and redirects to `/dashboard`
- [ ] `POST /login` with a wrong password returns 200 with an error message; no session written
- [ ] `POST /login` with an unknown email returns 200 with the same error message as wrong password
- [ ] `POST /login` with a blank email or password returns 200 with an error message
- [ ] The email field is pre-filled with the submitted value on any login error
- [ ] `GET /logout` clears `session["user_id"]` and redirects to `/`
- [ ] `GET /logout` when not logged in does not crash — redirects to `/` cleanly
- [ ] All 8 pytest tests in `tests/test_login_logout.py` pass
