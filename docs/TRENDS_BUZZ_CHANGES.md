# Trends / Buzz — changes log

## Done

- [x] Buzzword cloud uses **Google Trends only** (no Bluesky)
- [x] Football-only keyword filter — expanded lists for players, events, emotions, tactics
- [x] Category filters seeded via curated WC buzz terms in Trends collector
- [x] Dense word-cloud layout (no bar chart toggle, no hover tooltips, no methodology link)
- [x] Search interest ranking chart — white tooltip text for scores

## Stashed for later (with explanations)

### Per-country Google Trends (not just worldwide)

**What it means:** Today every team query uses `geo=''` (worldwide average). Per-country mode would run separate Trends pulls per nation (e.g. USA, Brazil, England) so you can see *where* search interest is highest, not just globally.

**Why later:** Each extra region multiplies API calls and collection time (48 teams × N countries). Needs batching strategy and possibly paid Trends limits.

---

### Region selector on the UI

**What it means:** A dropdown on the Trends page — e.g. Worldwide / United States / United Kingdom / Mexico — that reloads the ranking chart and word cloud for that region.

**Why later:** Depends on per-country data being collected and stored with a `region` column (partially exists in `trends_snapshots` but not populated per country yet).

---

### Team Trends sparklines

**What it means:** A small line chart next to each team showing how search interest changed over the last 7–30 days (not just today’s 0–100 score).

**Why later:** Requires storing daily Trends history (we insert snapshots but UI doesn’t chart history yet). Needs `/api/trends/{team}/history` endpoint.

---

### Clickable words → filter by keyword

**What it means:** Clicking a word in the cloud (e.g. “penalty”) would filter the team ranking or drill into related teams/posts for that topic.

**Why later:** Needs click handlers, routing state, and API support to map keywords → teams. Word cloud is currently non-interactive by design.

---

### Bandwagon meter

**What it means:** Highlights teams whose Google Trends score jumped the most in the last 24–48 hours — “fastest rising search interest” before a match or after news.

**Why later:** Needs at least two collection days of Trends data and a derivative metric (today vs yesterday % change).

---

### Host nation bump

**What it means:** Compare USA, Mexico, and Canada search interest against their confederation baseline to quantify the “home crowd / host nation” search boost for 2026.

**Why later:** Needs per-country Trends (or host-country geo pulls) and a baseline comparison algorithm.

---

### Other (from roadmap)

- [ ] Compare 2–4 teams on one Trends line chart
- [ ] Subtitle explaining 0–100 score in plain English
- [ ] Multi-word phrase extraction for Trends related queries
- [ ] Keyword co-occurrence graph
- [ ] Match-day overlay (football-data.org kickoff API)
- [ ] Backfill `keyword_snapshots.source` on production Postgres if column missing
- [ ] Re-run daily collection after deploy so Trends buzzwords populate

**Removed (will not do):** Separate Bluesky buzz cloud — product decision: Trends page is Google Trends only.
