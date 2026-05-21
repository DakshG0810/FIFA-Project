# WC Dashboard

Real-time FIFA World Cup 2026 sentiment analytics dashboard tracking fan buzz,
search trends, and win probabilities across all 32 teams.

## Features

- Live fan sentiment tracking via Bluesky
- Google Trends search interest analysis
- Live betting odds and win probability tracker
- Team popularity and buzz volume insights
- Sentiment vs odds divergence detection
- Viral spike detector
- Real-time backend APIs
- Modular full-stack architecture

## Data Sources

| Source | What it provides | Cost |
|---|---|---|
| Bluesky public API | Fan posts + sentiment | Free, no key needed |
| Google Trends | Search interest 0-100 per team | Free, no key needed |
| The Odds API | Win probabilities from bookmakers | Free tier (500 req/mo) |

## Tech Stack

### Frontend
- React + TypeScript
- Tailwind CSS
- Vite
- Recharts

### Backend
- FastAPI + Python
- APScheduler
- VADER sentiment analysis
- SQLite (local) → PostgreSQL (production)
- Uvicorn

## Project Structure

```
wc-dashboard/
│
├── .env.example
├── .gitignore
├── README.md
│
├── backend/
│   ├── database.py
│   ├── teams.py
│   ├── scheduler.py
│   ├── api.py
│   ├── requirements.txt
│   └── collectors/
│       ├── __init__.py
│       ├── bluesky.py
│       ├── google_trends.py
│       └── odds.py
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── .env.local
    └── src/
        ├── App.tsx
        ├── api.ts
        ├── main.tsx
        ├── index.css
        ├── vite-env.d.ts
        ├── types/
        │   └── index.ts
        ├── hooks/
        │   └── useApi.ts
        ├── components/
        │   ├── Navbar.tsx
        │   ├── StatCard.tsx
        │   ├── SentimentBar.tsx
        │   ├── TeamFlag.tsx
        │   ├── LoadingSkeleton.tsx
        │   └── DataFreshnessBar.tsx
        └── pages/
            ├── Overview.tsx
            ├── Sentiment.tsx
            ├── Odds.tsx
            ├── Trends.tsx
            └── Analytics.tsx
```

## Environment Variables

Create a `.env` file in the root `wc-dashboard/` folder:

```
ODDS_API_KEY=your_odds_api_key_here
DATABASE_URL=
ENV=development
BLUESKY_HANDLE=your.handle.bsky.social
BLUESKY_APP_PASSWORD=your-app-password
BLUESKY_DEMO_FALLBACK=true
```

Create a `.env.local` file in the `frontend/` folder:

```
VITE_API_URL=http://localhost:8000
```

Get your free Odds API key at: https://the-odds-api.com

## Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Initialise database (run once)
python database.py

# Terminal 1 — data collector (runs every 30 min automatically)
python scheduler.py

# Terminal 2 — API server
uvicorn api:app --reload
```

Backend runs on: http://localhost:8000
API docs at: http://localhost:8000/docs

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

## API Endpoints

| Endpoint | Description |
|---|---|
| GET /api/status | Health check + last collection times |
| GET /api/leaderboard | Combined team rankings |
| GET /api/sentiment | Sentiment per team |
| GET /api/sentiment/{team}/history | Time series for one team |
| GET /api/odds | Win probabilities |
| GET /api/trends | Google Trends scores |
| GET /api/keywords | Top buzzwords |
| GET /api/spikes | Viral spike alerts |

## Collaboration Workflow

```bash
git pull
git add .
git commit -m "your message"
git push
```

## Important — never push these to GitHub

- `node_modules/`
- `venv/`
- `.env`
- `.env.local`

Already handled in `.gitignore`.

## Deployment

- **Backend:** Render.com (free tier)
- **Frontend:** Vercel (free tier)
- **Database:** Render PostgreSQL (free, set DATABASE_URL env var)

## Development Status

### Completed
- Full project architecture
- Backend data collectors (Bluesky, Google Trends, Odds API)
- FastAPI with 8 endpoints
- SQLite/PostgreSQL auto-switching
- React frontend with 5 pages and 6 components
- Tailwind + Recharts configuration
- Sentiment analysis pipeline (VADER)

### Pending
- Live data verification and testing
- Deployment to Render + Vercel
- Real-time dashboard polish
- Match-level analytics
- LinkedIn share cards
