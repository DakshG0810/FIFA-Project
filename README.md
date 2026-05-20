# WC Dashboard

Real-time FIFA World Cup sentiment analytics dashboard built using React, FastAPI, NLP, and social media trend analysis.

---

## Features

- Live public sentiment tracking
- Google Trends analysis
- Betting odds monitoring
- Team popularity insights
- Analytics dashboard
- Real-time backend APIs
- Modular full-stack architecture

---

## Tech Stack

### Frontend
- React
- TypeScript
- Tailwind CSS
- Vite
- Bun

### Backend
- FastAPI
- Python
- SQLite / PostgreSQL
- Uvicorn

---

## Project Structure

```text
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
│   │
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
    │
    └── src/
        ├── App.tsx
        ├── api.ts
        ├── main.tsx
        ├── index.css
        ├── vite-env.d.ts
        │
        ├── types/
        │   └── index.ts
        │
        ├── hooks/
        │   └── useApi.ts
        │
        ├── components/
        │   ├── Navbar.tsx
        │   ├── StatCard.tsx
        │   ├── SentimentBar.tsx
        │   ├── TeamFlag.tsx
        │   ├── LoadingSkeleton.tsx
        │   └── DataFreshnessBar.tsx
        │
        └── pages/
            ├── Overview.tsx
            ├── Sentiment.tsx
            ├── Odds.tsx
            ├── Trends.tsx
            └── Analytics.tsx
```

---

## Frontend Setup

### Navigate to frontend

```bash
cd frontend
```

### Install dependencies

```bash
bun install
```

### Start frontend server

```bash
bun run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

## Backend Setup

### Navigate to backend

```bash
cd backend
```

### Create virtual environment

```bash
python -m venv venv
```

### Activate virtual environment

#### Windows

```bash
venv\Scripts\activate
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

### Start backend server

```bash
uvicorn api:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

## Environment Variables

Create a `.env` file in the root directory.

Example:

```env
REDDIT_CLIENT_ID=
REDDIT_SECRET=
TWITTER_BEARER_TOKEN=
```

---

## Collaboration Workflow

Pull latest changes:

```bash
git pull
```

Push new changes:

```bash
git add .
git commit -m "your message"
git push
```

---

## Important Notes

Do not push the following to GitHub:

- `node_modules/`
- `venv/`
- `.env`

These are already handled in `.gitignore`.

---

## Current Development Status

- Frontend architecture setup completed
- Backend architecture setup completed
- Tailwind configuration completed
- API structure setup completed

Pending:
- Live sentiment ingestion
- NLP pipeline
- Real-time analytics
- Dashboard visualizations
- Match-level analytics
- Team prediction engine