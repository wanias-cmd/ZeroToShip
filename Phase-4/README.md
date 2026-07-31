# TradePost — Phase 4: Static Visual Presentation Layer

This phase is the presentation layer built entirely with static HTML and
CSS grid — no live server, no real data, no working forms. Per the
assignment's competition protocol, everything here runs against hardcoded
mock data so the visual design can be built and reviewed independently of
the backend.

## What's inside

- **`templates/marketplace.html`** — the Trading Board. A CSS grid gallery
  of item cards, each showing a title, description, lister ID, and a
  status stamp (`Open` / `Traded`). Every form selector and button on this
  page is intentionally `disabled` — they exist purely as visual mockups
  of what the real, connected marketplace will look like.
- **`templates/dashboard.html`** — the Negotiation Status Dashboard. A list
  of mock active trade discussions, each showing a colored, high-visibility
  badge indicating whose turn it is: a glowing gold **Your Turn** badge, a
  red **Waiting for Peer** badge, plus **Accepted** and **Declined** states
  for completeness — all driven purely by CSS classes on hardcoded mock
  data, no backend logic involved.
- **`static/css/marketplace.css`** — the shared stylesheet for both pages,
  continuing the ledger/trading-post visual theme (stamped status marks,
  dashed ticket borders) established in earlier phases for visual
  consistency across the whole project.

## Project structure

```
Phase-4/
├── templates/
│   ├── marketplace.html    # Trading Board — mock item cards
│   └── dashboard.html      # Negotiation dashboard — mock turn-state badges
├── static/
│   └── css/
│       └── marketplace.css
└── Output/                  # Screenshots of both pages rendered
```

## Viewing it

No server required — these are plain static files. Just open either HTML
file directly in a browser:

```
templates/marketplace.html
templates/dashboard.html
```

## Design notes

- **Marketplace grid**: `display: grid; grid-template-columns:
  repeat(auto-fill, minmax(240px, 1fr));` — responsive card layout that
  reflows automatically based on available width.
- **Status stamps**: rotated, bordered badges (`Open` in brass, `Traded`
  in muted rust) echo a rubber-stamped ledger entry.
- **Turn-state badges**: color and a glow (`box-shadow`) distinguish
  urgency at a glance — gold/glowing for "it's your move," red/flat for
  "waiting."

## Screenshots

See `Output/` for the rendered marketplace grid and negotiation dashboard.
