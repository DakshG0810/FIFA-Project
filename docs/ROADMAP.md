# PulseCup — Roadmap & How Live Data Works

## How data flows (you do NOT call APIs from the browser)

```
┌─────────────┐     every 60 min      ┌──────────────┐     read only     ┌──────────────┐
│  Scheduler  │ ──► Bluesky/Odds/    │   SQLite /   │ ◄────────────── │   FastAPI    │
│  (worker)   │     Trends APIs      │  PostgreSQL  │                 │   :8000      │
└─────────────┘                      └──────────────┘                 └──────┬───────┘
                                                                             │
                                                                    poll every 30–60s
                                                                             ▼
                                                                      ┌──────────────┐
                                                                      │  React UI    │
                                                                      │  :5173       │
                                                                      └──────────────┘
```

- **Collectors** fetch external APIs and **write** to the database.
- **FastAPI** only reads the database (fast, no rate limits in the UI).
- **Frontend** refreshes from your API on a timer — it never hits Bluesky/Google/Odds directly.

You do **not** need to manually run API calls while using the dashboard. You only need the **scheduler running** (locally or on Render).

---

## Why you see DEMO / CACHED today

| Badge | Meaning |
|-------|---------|
| **LIVE** | Collector ran recently (< 2h) with real external data |
| **CACHED** | Real data, but last run is older than 2h |
| **DEMO** | Bluesky public API blocked (403) → synthetic posts used |

**Fix for live Bluesky:** add `BLUESKY_HANDLE` + `BLUESKY_APP_PASSWORD` to `.env`, set `BLUESKY_DEMO_FALLBACK=false`.

---

## Recommended schedule

| Environment | Interval | Notes |
|-------------|----------|-------|
| **Render (production)** | **24 hours** | All three collectors in one job — saves free tier |
| Local testing | `COLLECT_INTERVAL_HOURS=1` in `.env` | Hourly pulse while developing |

Configured in `backend/scheduler.py` via `COLLECT_INTERVAL_HOURS`.

---

## Production on Render (no laptop needed)

Deploy **free** stack:

1. **Web Service** (Render free) — `uvicorn api:app` serves the API
2. **PostgreSQL** (Render free) — `DATABASE_URL` (shared cloud DB)
3. **GitHub Actions** — `.github/workflows/daily-collect.yml` runs collectors once per day (no paid Render worker)

Frontend on **Vercel** with `VITE_API_URL=https://your-api.onrender.com`.

You do **not** keep your PC on.

---

## Phase plan

### Phase 1 — Live data (now)
- [x] Hourly Bluesky schedule
- [x] Status API reports LIVE / CACHED / DEMO per source
- [x] Map flags + top 5 tooltip
- [x] Scattered word cloud layout
- [ ] Bluesky app password for true LIVE posts
- [ ] Real Google Trends by country (batch job, slow)

### Phase 2 — Production deploy
- [ ] Render: API + worker + Postgres
- [ ] Vercel: frontend
- [ ] `render.yaml` + env vars documented

### Phase 3 — Deeper analytics
- [ ] Match-day overlay (football-data.org kickoff lines)
- [ ] Pre/post match sentiment swing table
- [ ] Team vs team sentiment battles
- [ ] Confederation aggregate index
- [ ] “Dark horse” detector (low odds + high sentiment)
- [ ] Export snapshot / LinkedIn share card

### Phase 4 — Polish
- [ ] Remove hardcoded DEMO badges → driven by `/api/status`
- [ ] Email/Slack alert on viral spikes
- [ ] Historical playback (rewind 7 days)

---

## New analysis ideas (high value)

1. **Momentum index** — compound × mention velocity (6h derivative)
2. **Controversy score** — high mentions + negative compound + VAR cluster volume
3. **Host nation bump** — USA/Mexico/Canada vs baseline for CONCACAF
4. **Bandwagon meter** — teams whose trends_score grew fastest in 24h
5. **Echo chamber** — % posts from top 20 influencers per team
6. **Sentiment–odds arbitrage** — sustained divergence over 48h
7. **Keyword co-occurrence graph** — which words appear together
8. **Knockout stress index** — sentiment volatility pre-match
