# PulseCup — Plan forward (updated)

Work **one step per session** when building features. **Deploy (Step 6)** can be done now so the team shares cloud data.

---

## Status overview

| Step | What | Status |
|------|------|--------|
| **1** | Geographic map — flags, contrast, stable pins | **Done** (flagcdn URL + SVG `<image>` fix) |
| **2** | Word cloud — 80+ words, richer layout | **Pending** |
| **3** | Six insights (momentum, controversy, dark horse, bandwagon, echo chamber, keyword graph) | **Pending** |
| **4** | Bluesky LIVE (app password in `.env`) | **Done** |
| **5** | Team workflow — Git + shared DB story | **Ready** — see `docs/TEAM_GITHUB.md` |
| **6** | Deploy Render (API + Postgres) + GitHub Actions daily + Vercel | **Ready** — see `docs/DEPLOY_RENDER.md` |

---

## Phase A — Production (do now)

You can close your laptop after this:

1. Push repo to GitHub (`docs/TEAM_GITHUB.md`).
2. Render Blueprint from `render.yaml` — **API + Postgres only** (no paid worker).
3. Set secrets on Render API: `ODDS_API_KEY`, `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`.
4. GitHub Actions secrets + run **Daily data collection** once (see `docs/DEPLOY_RENDER.md`).
5. Vercel deploy `frontend/` with `VITE_API_URL=https://your-api.onrender.com`.
6. Set `FRONTEND_URL` on Render API to your Vercel URL.

**Collection (production):** GitHub Actions **once per day** (free) — laptop not required.

---

## Phase B — Dashboard polish (next features)

### Step 2 — Word cloud
- Raise keyword limit to 80+ in API + `BuzzwordCloud.tsx`
- Tune spiral / font scaling for density

### Step 3 — Six insight modules
| Module | Idea | Likely home |
|--------|------|-------------|
| Momentum index | compound × mention velocity (6h) | Overview / Sentiment |
| Controversy score | high mentions + negative compound | Analytics |
| Dark horse | low odds + rising sentiment | Odds |
| Bandwagon meter | fastest 24h trends growth | Trends |
| Echo chamber | % reach from top influencers | Analytics |
| Keyword co-occurrence graph | word pairs from posts | Trends |

Each needs: backend metric endpoint → small React card/chart.

---

## Phase C — Later (roadmap)

- Real per-country Google Trends (replace hash jitter on map)
- Match-day overlay (football-data.org)
- Pre/post match sentiment swing
- Team vs team battles
- Confederation index
- Export / LinkedIn share card
- Spike alerts (email/Slack)
- 7-day historical playback

Full list: `docs/ROADMAP.md`.

---

## Local vs cloud

| | Local laptop | Render production |
|--|--------------|-------------------|
| Database | SQLite `wc_dashboard.db` | PostgreSQL |
| Collectors | `python scheduler.py` (optional) | Background worker 24/7 |
| API | `uvicorn api:app --reload` | Web Service |
| Frontend | `npm run dev` | Vercel |
| Refresh | Default **24h** (set `COLLECT_INTERVAL_HOURS=1` in `.env` to test hourly) | **24h** |

---

## Quick links

- Bluesky setup: `docs/BLUESKY_SETUP.md`
- Render deploy: `docs/DEPLOY_RENDER.md`
- Git team flow: `docs/TEAM_GITHUB.md`
