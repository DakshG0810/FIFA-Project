# Deploy PulseCup — FREE (no card for worker)

| Piece | Where | Cost |
|-------|--------|------|
| **API** | Render Web Service (free) | $0 |
| **Database** | Render PostgreSQL (free) | $0 |
| **Daily collectors** | GitHub Actions (free) | $0 |
| **Frontend** | Vercel (free) | $0 |

Your laptop can stay off. GitHub runs collectors once per day; Render serves the API.

---

## Architecture

```
GitHub Actions (daily)  ──writes──►  Render Postgres  ◄──reads──  Render API
                                              ▲
                                              │
                                    Vercel frontend (browser)
```

---

## Step 1 — Render (API + database only)

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.
2. Connect **`DakshG0810/FIFA-Project`** (repo owner’s GitHub — not unrelated accounts).
3. Blueprint creates **pulsecup-api** + **pulsecup-db** only (no worker → **no card** for a worker).
4. When asked for secrets on **pulsecup-api**, set:
   - `ODDS_API_KEY`
   - `BLUESKY_HANDLE`
   - `BLUESKY_APP_PASSWORD`
5. Deploy. Open `https://pulsecup-api.onrender.com/api/status` → `"status": "ok"`.

**Note:** Free API sleeps after ~15 min idle; first request may take ~30s to wake.

---

## Step 2 — GitHub Actions secrets (daily collection)

Repo owner (**daksh08**) or anyone with **Admin** on the repo:

1. GitHub → **FIFA-Project** → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these **four** secrets:

| Secret name | Value |
|-------------|--------|
| `DATABASE_URL` | Render → **pulsecup-db** → **Connections** → **External Database URL** (copy full string) |
| `ODDS_API_KEY` | From your `.env` |
| `BLUESKY_HANDLE` | From your `.env` |
| `BLUESKY_APP_PASSWORD` | Bluesky **app password** (not login password) |

Use the **External** URL, not Internal — Actions runs outside Render.

---

## Step 3 — Run collection once (don’t wait until tomorrow)

1. GitHub → **Actions** tab → **Daily data collection** → **Run workflow** → **Run workflow**.
2. Wait ~5–15 minutes (Bluesky is slow).
3. Green checkmark = success.
4. Refresh `https://pulsecup-api.onrender.com/api/status` → `last_bluesky` should have a recent time.

Schedule: **06:00 UTC daily** (edit `.github/workflows/daily-collect.yml` to change).

---

## Step 4 — Vercel (frontend)

1. [vercel.com](https://vercel.com) → import **FIFA-Project** repo.
2. **Root Directory:** `frontend`
3. Env: `VITE_API_URL` = `https://pulsecup-api.onrender.com` (your real Render URL)
4. Deploy → copy Vercel URL → Render **pulsecup-api** → `FRONTEND_URL` → redeploy.

---

## Teammates

- Clone repo, `frontend/.env.local` with `VITE_API_URL` pointing to Render.
- **No** database download, **no** API keys for frontend-only work.
- See `docs/TEAM_GITHUB.md`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Render asks for card | You selected a **paid** plan or old Blueprint with **worker** — use current `render.yaml` (API + DB only) |
| Actions fails on DB | `DATABASE_URL` must be **External** connection string |
| `bluesky: empty` after deploy | Run **Actions → Daily data collection** manually once |
| Actions not visible | Push `.github/workflows/daily-collect.yml` to `main` |
| CORS error | Set `FRONTEND_URL` on Render API to exact Vercel URL |
| Free Postgres expiry | Render free DBs have time limits — check Render docs / upgrade later if needed |

---

## Optional: test collectors locally

```bash
cd backend
# DATABASE_URL=... (external URL) in env
python run_collect_once.py
```
