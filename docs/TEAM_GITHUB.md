# Team workflow — GitHub + shared cloud data

## How it fits together

```
GitHub (code)          Render (data + API)           Vercel (UI)
     │                        │                          │
     ├─ teammates pull ───────┼── same DATABASE_URL ─────┤
     │                        │                          │
     └─ frontend/.env.local ──┴── VITE_API_URL ──────────┘
```

- **Git** = share code changes (React pages, API routes, fixes).
- **Render Postgres** = one database everyone reads via the API.
- **Your laptop** = optional for development only.

---

## One-time setup (project lead)

1. Create a GitHub repo (e.g. `pulsecup` or `FIFA-Project`).
2. From project root:

```bash
git init
git add .
git commit -m "Initial PulseCup dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_ORG/YOUR_REPO.git
git push -u origin main
```

3. Complete `docs/DEPLOY_RENDER.md` so API + DB are live and GitHub Actions runs daily collection.
4. Share with the team:
   - Repo URL
   - Vercel dashboard URL
   - Render API URL (`https://pulsecup-api.onrender.com`)

**Never commit:** `.env`, `.env.local`, `wc_dashboard.db`, `node_modules/`, `venv/`.

---

## Teammate daily workflow

```bash
git pull origin main
cd frontend
npm install
# .env.local once:
# VITE_API_URL=https://pulsecup-api.onrender.com
npm run dev
```

Open http://localhost:5173 — data comes from Render, not their machine.

### Making changes

```bash
git checkout -b feature/my-change
# edit files
git add .
git commit -m "Add buzz chart filter"
git push -u origin feature/my-change
```

Open a Pull Request on GitHub → review → merge to `main` → Vercel auto-redeploys frontend.

Backend changes: merge to `main` → Render auto-redeploys API; collectors run on the daily Actions schedule.

---

## Who needs API keys?

| Person | Odds / Bluesky keys? |
|--------|----------------------|
| Teammates (frontend only) | No |
| Teammates (backend collectors locally) | Only if testing collectors on laptop |
| Render (production API) | Yes — set in Render dashboard |
| GitHub Actions (daily collect) | Yes — repo **Secrets** (`DATABASE_URL` external, Odds, Bluesky) |

---

## Local backend (optional)

Only if someone is changing collectors or API:

```bash
cd backend
pip install -r requirements.txt
# copy .env.example → ../.env and fill keys
uvicorn api:app --reload
```

Use SQLite locally (`DATABASE_URL` blank). Production always uses Postgres on Render.
