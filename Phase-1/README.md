# TradePost — A Web-Based Peer-to-Peer Barter Exchange

TradePost is a lightweight web app where users list items and swap them with
each other — no cash involved. It's built with Flask, using a flat JSON file
as a simple stand-in for a relational database.

## What it does

- **List an item** you want to trade.
- **Browse the board** of everything currently up for trade.
- **Make an offer** on someone else's listing.
- **Accept an offer** as the listing's owner — this automatically declines
  every other pending offer on that listing and marks it as traded.

## Core concepts this project covers

- Defining data models (`Post`, `NegotiationOffer`) with serialization
  methods (`to_dict()` / `from_dict()`) that translate Python objects to and
  from a JSON flat-file, acting as a lightweight substitute for a real
  database.
- Building a Flask backend with both a JSON API (for programmatic testing)
  and an HTML frontend (for browser use), sharing the same underlying data
  and business logic.
- Session-based identity: a logged-in user's ID is stored server-side in a
  signed cookie, so routes always know who's acting without trusting
  client-supplied data.
- Atomic business rules enforced server-side: offers can't be made on
  closed listings, accepting one offer cascades to auto-decline the rest,
  and a listing closes the moment a trade is accepted.

## Project structure

```
Phase-1/
├── app.py                # Flask app: all routes (API + HTML)
├── db.py                 # load_db() / save_db() — reads and writes the JSON flat-file
├── models/
│   ├── post.py            # Post model + to_dict()/from_dict()
│   └── offer.py           # NegotiationOffer model + to_dict()/from_dict()
├── templates/             # Jinja2 HTML templates (base, login, board, ticket detail)
├── static/
│   └── style.css          # Visual styling
├── requirements.txt        # Python dependencies
└── Output/                 # Screenshots demonstrating the app in action
```

## Data models

**Post** (`models/post.py`)
| Field | Type | Description |
|---|---|---|
| `post_id` | int | Unique identifier |
| `title` | str | Item title |
| `description` | str | Item description |
| `owner_id` | int | ID of the user who listed it |
| `status` | str | `"Open"` or `"Traded"` |

**NegotiationOffer** (`models/offer.py`)
| Field | Type | Description |
|---|---|---|
| `offer_id` | int | Unique identifier |
| `post_id` | int | The post this offer is against |
| `proposer_id` | int | ID of the user making the offer |
| `offered_item_details` | str | What's being offered in trade |
| `turn_holder_id` | int | Whose turn it is to act next |
| `status` | str | `"Pending"`, `"Accepted"`, or `"Declined"` |

Both models implement `to_dict()` and `from_dict()`, which map instances
directly to and from plain dictionaries for JSON serialization into
`tradepost_db.json`.

## Routes

### HTML pages (session-based)
| Method | Path | What it does |
|---|---|---|
| GET/POST | `/login` | Sets `session["user_id"]` |
| GET | `/logout` | Clears the session |
| GET | `/` | The trade board — lists all posts |
| POST | `/posts/create` | Creates a post from a form submission |
| GET | `/posts/<post_id>` | View a single post + its offers |
| POST | `/posts/<post_id>/offers/create` | Submit an offer via form |
| POST | `/posts/<post_id>/offers/<offer_id>/accept-form` | Accept an offer via form |

### JSON API
| Method | Path | What it does |
|---|---|---|
| GET | `/posts` | Returns all posts as JSON |
| POST | `/posts` | Creates a post from a JSON body |
| GET | `/api/posts/<post_id>` | Returns a single post as JSON |
| GET | `/posts/<post_id>/offers` | Returns all offers on a post |
| POST | `/posts/<post_id>/offers` | Creates an offer from a JSON body |
| POST | `/posts/<post_id>/offers/<offer_id>/accept` | Accepts an offer, cascades declines |

## Running it locally

```bash
# from inside Phase-1/
pip install -r requirements.txt
python app.py
```

Then visit `http://127.0.0.1:5000/login` in a browser.

## Testing the JSON API directly

```bash
curl -X POST http://127.0.0.1:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Guitar for Bike", "description": "Acoustic guitar, good condition", "owner_id": 101}'
```

## Screenshots

See the `Output/` folder for screenshots demonstrating the app's core flows:
listing an item, making an offer, and accepting an offer (with the cascade
auto-decline visible on a second, competing offer).
