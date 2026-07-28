# TradePost — Phase 3: RESTful Negotiation API & Turn-Taking Logic

This phase separates TradePost's business rules from its HTTP layer, and
adds real turn-based negotiation: either party can submit a counter-offer,
which flips whose turn it is to respond, enforced strictly server-side.

## What it adds on top of Phase 2

- **`models/logic.py`** — pure business-rule functions, independent of
  Flask or HTTP. Every function returns a consistent
  `(result, error_message, status_code)` tuple, so callers never have to
  guess how to interpret success vs. failure.
- **`views/routes.py`** — a Blueprint of thin RESTful routes under
  `/api/*`. Each route loads the data, calls one `logic.py` function,
  and translates the result into a JSON response. No business logic lives
  in the routes themselves.
- **Counter-offers** — a genuinely new mechanic. Submitting a counter
  flips `turn_holder_id` between the post owner and the proposer. Trying
  to counter when it isn't your turn is rejected with `403 Forbidden`.

## Project structure

```
Phase-3/
├── app.py                # Registers auth_bp and api_bp blueprints
├── db.py
├── models/
│   ├── post.py
│   ├── offer.py
│   └── logic.py            # Business rules: create_offer, submit_counter_offer,
│                            #   accept_offer, get_open_posts
├── views/
│   ├── auth.py              # From Phase 2
│   └── routes.py            # RESTful /api endpoints
├── requirements.txt
└── Output/                   # Screenshots demonstrating the full negotiation flow
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/posts` | Returns only listings with `status: "Open"` |
| POST | `/api/offers` | Submits a new offer against a post |
| POST | `/api/offers/<offer_id>/counter` | Submits a counter-offer; flips `turn_holder_id` |
| POST | `/api/posts/<post_id>/offers/<offer_id>/accept` | Accepts an offer; cascades auto-decline to rivals, closes the post |

## Turn-taking & auto-decline rules

- An offer is created with `turn_holder_id` set to the post's owner —
  it's their turn to respond.
- A counter-offer can only be submitted by whoever currently holds the
  turn (`actor_id == turn_holder_id`); otherwise the request is rejected
  with `403`.
- Each successful counter flips `turn_holder_id` to the other party.
- Accepting an offer sets it to `"Accepted"`, auto-declines every other
  `"Pending"` offer on the same `post_id` by querying and updating the
  JSON array directly, and flips the post's `status` to `"Traded"`.

## Testing the full negotiation sequence (curl / Postman)

```bash
# 1. See what's open
curl http://127.0.0.1:5000/api/posts

# 2. Make an offer
curl -X POST http://127.0.0.1:5000/api/offers \
  -H "Content-Type: application/json" \
  -d '{"post_id": 6, "proposer_id": 202, "offered_item_details": "A lamp, works great"}'

# 3. Counter, as the current turn holder (the post owner)
curl -X POST http://127.0.0.1:5000/api/offers/6/counter \
  -H "Content-Type: application/json" \
  -d '{"offered_item_details": "Lamp plus $5 trade credit", "actor_id": 1}'

# 4. Try countering out of turn -> 403
curl -X POST http://127.0.0.1:5000/api/offers/6/counter \
  -H "Content-Type: application/json" \
  -d '{"offered_item_details": "Nice try", "actor_id": 1}'

# 5. Accept
curl -X POST http://127.0.0.1:5000/api/posts/6/offers/6/accept
```

## Screenshots

See `Output/` for the full sequence above: filtered open listings, offer
creation, a successful in-turn counter, a rejected out-of-turn counter,
and the final accept with cascade.
