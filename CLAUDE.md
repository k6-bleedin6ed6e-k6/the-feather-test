# the-feather-test — Project Context

## What this is

A bird-themed Turing test web app. Three roles:
- **Ornithologist (judge)** — asks questions, guesses which respondent is the AI
- **Human bird** — joins with a room code, answers in character as a bird
- **AI bird** — Claude API locked into a species via system prompt, auto-responds

After 5 rounds the judge guesses. Reveal screen shows the answer and updates the leaderboard.

## Stack

- Python 3.12 / Flask / Flask-SocketIO (real-time via Socket.IO)
- Anthropic Claude API — `claude-haiku-4-5-20251001` (fast, cheap, stays in character well)
- SQLite (`feather.db`) — session and score persistence
- Jinja2 templates + vanilla CSS + vanilla JS (no React, no Tailwind)
- Render for hosting

## Repo

`github.com/kwasikontor45/the-feather-test`
Local path: `~/local-lab/the-feather-test/`

## Run locally

```bash
cd ~/local-lab/the-feather-test
source venv/bin/activate
python3 run.py
```

Server at `http://localhost:5000`.

## Deploy

Render — `render.yaml` is configured. Push to GitHub, connect on Render, set `ANTHROPIC_API_KEY`.

## Key files

| File | Purpose |
|---|---|
| `app/__init__.py` | Flask app factory, SocketIO init, DB init |
| `app/ai_bird.py` | Claude API call — takes species + question, returns bird reply |
| `app/sockets.py` | All Socket.IO event handlers (judge_join, bird_join, send_question, bird_reply) |
| `app/routes/game_routes.py` | HTTP routes + in-memory `active_rooms` dict |
| `app/routes/api_routes.py` | REST endpoint: POST /api/bird-response |
| `app/db/store.py` | SQLite helpers: create/get/complete session, leaderboard |
| `app/species/species-config.json` | Bird roster: crow, robin, pigeon, parrot |
| `app/templates/` | Jinja2 templates — base, index, game-view, bird-view, reveal, leaderboard |
| `app/static/js/chat-ui.js` | Judge's Socket.IO client |
| `app/static/js/bird-ui.js` | Human bird's Socket.IO client |
| `app/static/css/main.css` | All styles — dark ornithology lab aesthetic |

## Architecture

**Room lifecycle:**
1. Judge hits `POST /create` → random species assigned → random Bird A/B assignment → room stored in `active_rooms` dict + SQLite
2. Judge goes to `/game/<room_code>`, emits `judge_join` via Socket.IO
3. Human bird hits `/join`, enters room code, goes to `/bird/<room_code>`, emits `bird_join`
4. Judge types a question → `send_question` event → broadcast to human bird + Claude API called in background thread
5. Both replies routed back to judge as Bird A or Bird B (assignment is fixed per session)
6. After 5 rounds, judge submits guess → `/reveal/<room_code>?guess=A|B` → scoring recorded

**Bird A/B assignment:**
- `human_is_bird_a = True` → human = Bird A, AI = Bird B
- `human_is_bird_a = False` → human = Bird B, AI = Bird A
- Assigned randomly on room creation, stored in `active_rooms` and SQLite

**`active_rooms` dict** is in-memory — resets on server restart. SQLite holds the persistent record. For multi-worker production, this would need Redis; single-worker Render deploy is fine as-is.

## Naming conventions

- Python files: `snake_case`
- HTML/CSS/JS files: `kebab-case`
- JSON keys: `kebab-case`

## Environment

```
ANTHROPIC_API_KEY=...   # in .env (gitignored)
SECRET_KEY=...          # in .env (gitignored)
```

## Known limitations / future work

- `active_rooms` is in-memory — doesn't survive server restart, not multi-worker safe
- No authentication — anyone with a room code can join as the bird
- AI history (`room['history']`) grows unbounded — fine for 5 rounds
- Add more species in `species-config.json` — no code changes needed
