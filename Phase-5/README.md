# TradePost — A Web-Based Peer-to-Peer Barter Exchange

TradePost is a full-stack Flask web app where users list items and trade
them with each other — no cash involved. This is the final, fully
integrated build: every mock view has been replaced with live data, every
route is backed by real authentication, and the whole negotiation
lifecycle (offer → counter → accept → cascade-decline) runs end to end.

## Tech stack

- **Backend:** Python, Flask (Blueprints for modular routing)
- **Data layer:** A JSON flat-file (`tradepost_db.json`) acting as a
  lightweight relational store, read/written through `db.py`
- **Auth:** Flask sessions (signed cookies) + Werkzeug password hashing
- **Frontend:** Jinja2 templates with template inheritance, vanilla CSS
  (custom ledger/trading-post visual theme, CSS Grid layouts)
- **Testing:** curl (Postman-equivalent) for the JSON API, browser
  testing for the full user-facing flow

## Project structure

```
Phase-5/
├── app.py                  # Flask app: page routes, wires all blueprints together
├── db.py                   # load_db() / save_db() — the persistence layer
├── models/
│   ├── post.py               # Post model + to_dict()/from_dict()
│   ├── offer.py               # NegotiationOffer model + to_dict()/from_dict()
│   └── logic.py                # Business rules: create_offer, submit_counter_offer,
│                                #   accept_offer, get_open_posts — used by both the
│                                #   JSON API and the HTML routes
├── views/
│   ├── auth.py                 # /register, /login, login_required decorator
│   └── routes.py                # RESTful /api/* endpoints
├── templates/                # All pages: login, marketplace board, post detail,
│                              #   negotiation dashboard
├── static/
│   └── style.css              # Shared visual theme across every page
├── requirements.txt
└── Output/                    # Screenshots demonstrating the full live app
```

## How to install and run

```bash
# from inside Phase-5/
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in a browser. You'll be redirected to
the login page automatically.

## How to test the full feature set

**1. Register two accounts** (you'll need two to test negotiation — one
user can't trade with themselves):
```bash
curl -X POST http://127.0.0.1:5000/register -H "Content-Type: application/json" -d '{"username": "alice", "password": "trade123"}'
curl -X POST http://127.0.0.1:5000/register -H "Content-Type: application/json" -d '{"username": "bob", "password": "swap456"}'
```

**2. Log in as alice** at `/login` in the browser.

**3. List an item** using the "List something to trade" form on the
homepage. It appears immediately on the marketplace grid.

**4. Log out, log in as bob.** Click into alice's listing and submit an
offer.

**5. Check "My Negotiations"** while still logged in as bob — the offer
shows a red **Waiting for Peer** badge (bob already moved; it's alice's
turn).

**6. Log back in as alice.** Check "My Negotiations" — the same offer now
shows a gold, glowing **Your Turn** badge.

**7. Accept the offer** from the post's detail page. This:
   - Marks the offer `Accepted`
   - Auto-declines every other pending offer on that post
   - Flips the post's status to `Traded`
   - Redirects back to the post, showing the final state live

**8. Try to break it** (validation checks):
   - As bob, try to accept your own offer — rejected (`400`), enforced
     server-side even if the UI already hides the button.
   - Try any write route (`POST /posts`, `POST /api/offers`, etc.)
     without logging in — every one returns `401 Authentication required`.
   - Submit a counter-offer out of turn via `POST
     /api/offers/<id>/counter` — rejected with `403`.

## Core features

- **Authentication** — real accounts, hashed passwords, session cookies
- **Marketplace board** — live CSS grid of open listings
- **Negotiation dashboard** — real-time turn-state badges per offer
- **Turn-taking** — counter-offers flip whose move it is; enforced,
  not just visual
- **Atomic accept + cascade** — accepting one offer auto-declines all
  competing offers on that post and closes the listing, in one
  transaction
- **Dual interface** — every core action is reachable both through the
  browser UI and a parallel JSON API, sharing the same underlying
  business logic in `models/logic.py`

## Screenshots

See `Output/` for the complete live flow: the marketplace grid, both
turn-state badges, a post's offer/accept view, and a finished trade.
