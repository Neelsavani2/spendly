# Spec: Backend Routes For Profile Page

## Overview
Step 04 built the profile page UI using fully hardcoded Python dicts. Step 05 replaces that
hardcoded data with real database queries, making the profile page show the logged-in user's
actual name, email, join date, spending totals, recent transactions, and category breakdown.
No schema changes are required — the existing `users` and `expenses` tables already hold
everything needed. All new query logic lives in `database/db.py`; the route in `app.py`
calls those helpers and passes their results straight to the existing template.

## Depends on
- Step 1: Database setup (users + expenses tables must exist)
- Step 2: Registration (real user rows must be creatable)
- Step 3: Login and Logout (session must carry a real `user_id`)
- Step 4: Profile Page (profile.html must already exist with the expected variable names)

## Routes
- `GET /profile` — already exists; replace hardcoded context with live DB data — logged-in only

No new routes.

## Database changes
No schema changes. Four new helper functions are added to `database/db.py`:

| Function | Purpose |
|---|---|
| `get_profile_stats(user_id)` | Returns total_spent, this_month, transaction count, top_category |
| `get_recent_transactions(user_id, limit=5)` | Returns the N most-recent expense rows |
| `get_category_breakdown(user_id)` | Returns per-category totals + integer percentages |
| `format_currency(amount)` | Pure helper — formats a float as `"₹1,234"` |

## Templates
- **Modify:** `templates/profile.html` — no structural changes; update any hardcoded
  display strings that assumed the old dict shape (e.g. if `member_since` key name changes).
  The template variable names (`user`, `stats`, `transactions`, `categories`) stay identical.

## Files to change
- `database/db.py` — add the four helper functions above
- `app.py` — replace hardcoded dicts in the `/profile` route with calls to the new helpers;
  derive `member_since` from `user["created_at"]` using `datetime.strptime`

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()` only
- Parameterised queries only — never f-strings or `.format()` in SQL
- Passwords hashed with werkzeug (no auth changes in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `get_profile_stats` must compute `this_month` using `strftime('%Y-%m', date) = strftime('%Y-%m', 'now')` in SQL — do not filter in Python
- `get_category_breakdown` must compute percentages as `round(category_total / grand_total * 100)` in Python; return 0 for all categories if grand_total is 0
- `format_currency` must use Python's `f"₹{amount:,.0f}"` — no JS formatting
- The `/profile` route must still redirect to `/login` if `session.get("user_id")` is absent
- `member_since` must be derived from `user["created_at"]` (e.g. `"June 2026"`) — not hardcoded
- Keep the context dict keys identical to Step 4: `user`, `stats`, `transactions`, `categories`

## Definition of done
- [ ] Visiting `/profile` without a session redirects to `/login`
- [ ] Visiting `/profile` while logged in returns HTTP 200
- [ ] The displayed name and email match the logged-in user's actual DB record
- [ ] `member_since` reflects the real account creation date, not a hardcoded string
- [ ] The total spent stat matches the sum of all the user's expense rows
- [ ] The "this month" stat correctly sums only the current calendar month's expenses
- [ ] The transaction count stat matches the actual number of rows in `expenses` for the user
- [ ] The top category reflects the real highest-spend category for the user
- [ ] The recent transactions list shows the 5 most-recent expenses (date descending)
- [ ] The category breakdown percentages add up to approximately 100 (rounding is fine)
- [ ] A freshly registered user with no expenses sees `₹0` totals and empty lists, not an error
- [ ] All queries use `?` placeholders — no string interpolation in SQL
