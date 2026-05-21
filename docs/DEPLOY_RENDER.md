# Deploy PulseCup to Render (laptop can stay off)

This runs **three** things in the cloud:

| Piece | Render type | What it does |
|-------|-------------|--------------|
| **pulsecup-api** | Web Service | Serves `https://your-api.onrender.com/api/...` |
| **pulsecup-collector** | Background Worker | Collects Bluesky + Trends + Odds **once per day** |
| **pulsecup-db** | PostgreSQL (free) | Shared database for API + worker |

Teammates only need the **GitHub repo** + **Vercel frontend URL** pointing at your API. They do **not** need your `.env` or your laptop.

---

## Before you start

1. Push this project to **GitHub** (private repo is fine).
2. Have ready (from your local `.env`, **do not commit these**):
   - `ODDS_API_KEY`
   - `BLUESKY_HANDLE`
   - `BLUESKY_APP_PASSWORD`
3. Free tier limits: Web Service may sleep after ~15 min idle; first request wakes it (~30s). Worker stays up and runs the daily job.

---

## Step 1 — Create services from Blueprint

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.
2. Connect your GitHub repo.
3. Render reads `render.yaml` and creates API + Worker + Postgres.
4. When prompted, set **secret** env vars on **both** `pulsecup-api` and `pulsecup-collector`:
   - `ODDS_API_KEY`
   - `BLUESKY_HANDLE`
   - `BLUESKY_APP_PASSWORD`
5. On **pulsecup-api** only, set:
   - `FRONTEND_URL` = your Vercel URL later (e.g. `https://pulsecup.vercel.app`) — you can add this after Step 2.

Deploy. Wait until API shows **Live**. Open:

`https://pulsecup-api.onrender.com/api/status`

You should see `"status": "ok"`. After the worker’s first run (~5–15 min), `last_bluesky` will have a timestamp.

---

## Step 2 — Deploy frontend on Vercel

1. [vercel.com](https://vercel.com) → **Add New Project** → import the same GitHub repo.
2. **Root Directory:** `frontend`
3. **Environment variable:**
   - `VITE_API_URL` = `https://pulsecup-api.onrender.com` (your Render API URL, no trailing slash)
4. Deploy.

Copy the Vercel URL → Render → **pulsecup-api** → Environment → set `FRONTEND_URL` to that URL → **Save & redeploy**.

---

## Step 3 — Seed data (first run)

The worker runs all collectors **immediately on start**, then every **24 hours**.

Watch logs: Render → **pulsecup-collector** → **Logs**. Look for:

```
[Scheduler] Collection run — ...
[Bluesky] Done (LIVE) — 32 teams
```

If Bluesky fails, check app password (not login password): `docs/BLUESKY_SETUP.md`.

---

## Schedule & free tier

| Setting | Value | Where |
|---------|-------|--------|
| Collection interval | **24 hours** | `COLLECT_INTERVAL_HOURS` in `render.yaml` |
| “LIVE” badge window | **30 hours** | `DATA_STALE_HOURS` on API |

To collect more often locally only, add to root `.env`:

```env
COLLECT_INTERVAL_HOURS=1
DATA_STALE_HOURS=2
```

---

## What teammates do

```bash
git clone <your-repo>
cd frontend
npm install
cp .env.example .env.local   # edit VITE_API_URL to Render API URL
npm run dev
```

They **do not** run `scheduler.py` or need API keys — production worker fills the database.

See `docs/TEAM_GITHUB.md` for branch/PR workflow.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| API 502 / slow first load | Free tier cold start; wait ~30s and refresh |
| `bluesky: empty` | Worker not running or credentials missing on **worker** service |
| CORS error in browser | Set `FRONTEND_URL` on API to exact Vercel URL (https, no slash) |
| Postgres connection error | Ensure `DATABASE_URL` is linked from DB on both services |
| Odds empty | Set `ODDS_API_KEY` on worker + API |

---

## Optional: run one collection manually

Render → **pulsecup-collector** → **Shell** (if available on your plan):

```bash
python -c "from scheduler import run_all_collectors; run_all_collectors()"
```

Or trigger a **Manual Deploy** on the worker to restart (runs collectors on boot).
