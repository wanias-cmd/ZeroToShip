# TradePost — Phase 2: Authentication & Profile Gatekeepers

This phase adds real, headless authentication to the TradePost server —
password-based accounts and session cookies — plus middleware that blocks
any data-modifying request unless the caller is authenticated. It's
validated purely via API calls (curl/Postman), no browser required.

## What it adds on top of Phase 1

- **User accounts.** A new `users` list in `tradepost_db.json`, storing a
  hashed password per user (never plain text) via Werkzeug's
  `generate_password_hash` / `check_password_hash`.
- **`/register`** — creates a new account.
- **`/login`** — verifies credentials and stores `session["user_id"]` in a
  signed cookie.
- **`login_required`** — a decorator (the "Profile Gatekeeper") applied to
  every route that creates or modifies data. If there's no valid session,
  the request is rejected with `401 Authentication required` before the
  route's real logic ever runs.

## Project structure

```
Phase-2/
├── app.py                # Flask app; registers the auth blueprint and
│                          # applies login_required to write routes
├── db.py                 # load_db() / save_db()
├── models/
│   ├── post.py
│   └── offer.py
├── views/
│   ├── __init__.py
│   └── auth.py            # Blueprint: /register, /login, login_required
├── requirements.txt
└── Output/                 # Screenshots demonstrating the auth flow
```

## Gatekeeping in practice

| Route | Protected? |
|---|---|
| `POST /posts` (create post) | ✅ requires login |
| `POST /posts/<id>/offers` (create offer) | ✅ requires login |
| `POST /posts/<id>/offers/<id>/accept` | ✅ requires login |
| `GET /posts`, `GET /posts/<id>` | ❌ open — read-only |

## Running it locally

```bash
# from inside Phase-2/
pip install -r requirements.txt
python app.py
```

## Testing with curl (or Postman)

**1. Try a write without logging in — should be rejected:**
```bash
curl -X POST http://127.0.0.1:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "test", "owner_id": 999}'
# -> 401 {"error": "Authentication required"}
```

**2. Register:**
```bash
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "bob", "password": "swap456"}'
```

**3. Log in, saving the session cookie:**
```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "bob", "password": "swap456"}' \
  -c cookies.txt
```

**4. Retry the write, now sending the saved cookie — should succeed:**
```bash
curl -X POST http://127.0.0.1:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Vinyl Records", "description": "70s rock collection", "owner_id": 1}' \
  -b cookies.txt
# -> 201 Created
```

In Postman, the same flow works automatically once cookie jar / session
persistence is enabled — no manual `-c`/`-b` flags needed.

## Screenshots

See `Output/` for the full sequence: a blocked unauthenticated write,
successful registration, successful login, and a successful authenticated
write using the resulting session.
