# Analytics page — review notes (no implementation yet)

User is reviewing each subsection sequentially. Changes are noted here only.

---

## 1) Narrative Shift — what it does & why it adds little value today

### What it is supposed to do

- Let you pick **up to 4 teams** and compare how **fan sentiment** moves over time.
- Plots **compound sentiment** (−1 to +1) on the Y-axis from **Bluesky posts** (VADER), not Google Trends or odds.
- X-axis is **hourly buckets** over the **last 7 days** (`/api/narrative`).
- Goal: spot a **“narrative shift”** — e.g. sentiment jumps after injury news, a win, VAR controversy, or squad announcement.

### How the data is built (backend)

1. For each selected team, query `sentiment_snapshots` where `source = 'bluesky'`.
2. Group by hour: `substr(captured_at, 1, 13)` → one average `compound` per hour.
3. Merge teams into one timeline; frontend draws one line per team.

### Why it does not add value right now

| Issue | Detail |
|-------|--------|
| **Not really hourly** | Production collects **once per day** (GitHub Actions). “Hourly buckets” are mostly empty; you get ~1 point per day per team, not a smooth hourly narrative. |
| **Flat lines** | Daily averaged compound scores barely move between runs (often all teams sit in a narrow band ~0.1–0.3 positive). Chart looks like flat parallel lines (see screenshot). |
| **No narrative detection** | Despite the name, it does **not** detect topics, keywords, or events — only average post tone. No link to “injury”, “VAR”, etc. |
| **Sparse history** | With few collection days in the DB, the 7-day window may only have a handful of points — little to compare. |
| **Same collector batch** | All teams scraped in one run → similar post mix and similar sentiment levels, so lines cluster together. |
| **Misleading subtitle** | UI says “hourly buckets (7 days)” but effective resolution is **daily** at best in production. |

### Change to implement (confirmed)

- [ ] **Switch from hourly to daily buckets** — one data point per **collection day** per team (not `substr(captured_at, 1, 13)` hour).
- [ ] **X-axis span: first collection day → today** — use all available daily runs from when collection started until now (not a fixed 7-day window). As more daily GitHub Action runs complete, the chart grows left-to-right.
- [ ] **Backend** (`/api/narrative` in `api_analytics.py`): `GROUP BY substr(captured_at, 1, 10)`; derive `days`/cutoff from earliest Bluesky snapshot in DB (or pass through from first collection date).
- [ ] **Frontend** (`Analytics.tsx`): update subtitle — e.g. “Compound sentiment · up to 4 teams · one point per collection day”; format X-axis as dates (e.g. `Jun 1`, `Jun 2`).
- [ ] **Empty days**: only show days that actually have a collection run (no zero-fill gaps unless we want explicit gaps).

### Other possible directions (later)

- [ ] Overlay **topic cluster volume** or keyword spikes on the same chart.
- [ ] Show **mention volume** as second axis to separate “more talk” vs “more positive”.
- [ ] Detect shift: flag when compound moves more than X between consecutive collection days.
- [ ] Tooltip explaining data source and collection frequency.

---

## 2) Total Interest vs Odds Tracker (rename from “Sentiment vs Odds Divergence”)

### What it does today (to replace)

- Single list ranked by **sentiment rank vs odds rank** gap (`compound` from Bluesky vs bookmaker win %).
- Labels: “Fans more optimistic” / “Bookmakers more optimistic”.
- ⚡ when ranks differ by >5 positions.
- **Problem:** Uses sentiment, not **interest**; no convergence block; not a two-column divergence table.

### Change to implement (confirmed)

#### Rename & framing

- Section title: **Total Interest vs Odds Tracker** (or similar).
- Compare **odds ranking** vs **total interest ranking** — **not sentiment**.

#### Total interest ranking (new composite metric)

**Total interest** = combined fan/search attention, from:

| Source | Field | Rank by |
|--------|--------|---------|
| **Google Trends** | `trends_score` (0–100) | Search interest rank |
| **Bluesky** | `mentions` (total posts across collection runs) | Buzz / discussion rank |

**Proposed combined rank** (to confirm at implementation):

- Rank all 48 teams separately on Trends score and on Bluesky mentions (1 = highest).
- **Total interest rank** = average of the two ranks (lower average = more overall interest), *or* rank by normalised `(trends_pct + mentions_pct) / 2`.
- Only teams with **both** Trends and Bluesky data get a full composite; document fallback if one source missing.

**Methodology hover** (subtitle or `*` / “Methodology” link):

- Explain odds: tournament winner outrights, averaged across bookmakers.
- Explain total interest: Google Trends search interest + Bluesky post volume, combined into one rank.
- Explain convergence vs divergence columns (see below).
- No sentiment in this section.

#### Layout (top → bottom)

**A) Convergence list** (above the table)

Teams where **bookmakers and the public agree** — high win probability **and** high World Cup interest:

- **Criteria (draft):** odds rank ≤ top N (e.g. top 12) **and** total interest rank ≤ top N **and** `|odds_rank − interest_rank| ≤ threshold` (e.g. ≤ 3–5 places).
- Display: compact list/cards — team flag, name, odds rank, interest rank, win %.
- **Insight copy:** e.g. “Bookmakers and fans both tracking this team closely — aligned hype and expectations.”

**B) Divergence table** — **2 columns only**

| Left column | Right column |
|-------------|----------------|
| **Higher odds, lower interest** | **Higher interest, lower odds** |
| Win probability rank is strong; total interest rank is weaker | Total interest rank is strong; odds rank is weaker |
| **Insight:** Less fan/search appeal than results suggest — team may be **underrated by the crowd** or **flying under the radar** despite bookmaker confidence | **Insight:** More buzz than bookmakers price in — **fan favourite / dark horse** territory; public following exceeds betting expectations |
| Show: flag, team, Odds #, Interest #, win %, insight text | Same fields, opposite insight |

- Sort each column by magnitude of gap (`|odds_rank − interest_rank|`, descending).
- Optional ⚡ or emphasis when gap > 5 (keep existing visual language).
- Teams in **convergence** list excluded from divergence columns (or shown only in convergence).

#### Backend (new or extend API)

- [ ] New endpoint e.g. `GET /api/interest-odds` or extend leaderboard with `interest_rank`, `odds_rank`, `gap`, `bucket: convergence | underrated_interest | overrated_interest`.
- [ ] Compute Trends rank + Bluesky mentions rank → `total_interest_rank`.
- [ ] Join latest odds from `odds_snapshots` (48 teams).
- [ ] Return structured payload: `{ convergence: [...], underrated_by_fans: [...], overrated_by_fans: [...] }`.

#### Frontend (`Analytics.tsx`)

- [ ] Replace current divergence list with convergence strip + 2-column table.
- [ ] Flags via `TeamFlag` (not 2-letter codes).
- [ ] Methodology tooltip on section subtitle.
- [ ] Remove sentiment-based copy (“Fans more optimistic” → interest-based insights above).

#### Open questions for implementation

- Exact formula for composite interest rank (average rank vs weighted score).
- Thresholds: top N for “high” probability/interest; max rank gap for convergence.
- Minimum gap to appear in divergence columns (e.g. > 5 ranks).

---

## 3) Geographic Heatmap

### What it does today

- Map pins show the **WC team flag** with the highest “interest score” per country.
- UI badge: **Google Trends** (`useDataMode("google_trends")`).
- Hover tooltip: “Top 5 supported teams” with scores.
- Dropdown filters to one team’s footprint (subset of teams in `HIGHLIGHT_TEAMS`).

### Root cause — why the map looks wrong (Australia/Canada everywhere, blanks, no Ivory Coast in Ivory Coast)

**The map is not using real per-country Google Trends data.**

`/api/trends/regions` (`api_analytics.py`) currently:

1. Loads **worldwide** `trends_snapshots` only (`region = 'worldwide'`).
2. Loads **Bluesky** mention totals and adds `mentions // 2` into the same score.
3. Queries regional Trends rows (`region != 'worldwide'`) — but the **collector never writes these** (`google_trends.py` always saves `region='worldwide'`). So regional DB rows are **empty**.
4. For each of ~50 hardcoded `COUNTRY_CODES`, it **synthesises** per-country rankings:
   ```python
   jitter = md5(f"{country}{team}") % 35
   score = worldwide_trends + bluesky_mentions + jitter
   ```
5. Picks top team from that fake score. Result:
   - **No real geography** — same global leaders (often Australia, Canada, Iran, Mexico) win in most countries because worldwide + Bluesky dominate; jitter is only ±35.
   - **Many blank countries** — only ~50 ISO codes in `COUNTRY_CODES`; most of Africa, Asia, Europe absent (e.g. **Ivory Coast `CI`**, Algeria, Ghana, etc. not in list → no pin).
   - **Host nation logic missing** — Ivory Coast cannot be #1 in Côte d’Ivoire because there is no CI geo pull and no “own country boosts participant” rule.
6. Flag pins are **large** on map (`size = 32` active / `22` inactive px in SVG).

**Conclusion:** Badge says Google Trends; behaviour is **worldwide Trends + Bluesky + hash jitter**. User is correct to suspect Bluesky / fake geo.

### Changes to implement (confirmed)

#### 1) Reduce flag pin size

- [ ] Shrink map markers (e.g. active **18–20px**, inactive **14–16px** height; smaller shadow circle).
- [ ] Tooltip legend flag can stay ~16px.

#### 2) Real Google Trends per-country data (remove Bluesky from this section)

- [ ] **Collector** (`google_trends.py`): for each relevant **geo** (ISO country code), fetch Trends interest for WC team query batches; store in `trends_snapshots` with `region = '<ISO>'` (e.g. `CI`, `US`, `GB`).
- [ ] **API** (`/api/trends/regions`): rank teams using **only** `trends_snapshots` where `region = country_code` — **no Bluesky mentions**, no MD5 jitter.
- [ ] Expand country coverage: all participating nations’ home countries + major football markets + World Cup host nations (US, CA, MX) + reasonable global set (not just 50 codes).

#### 3) Geo fallbacks & variation (so map is plausible)

When per-country Trends is sparse or rate-limited:

- [ ] **Home country rule:** If `{Team}` is a WC participant, that team gets **#1 in their own country** (e.g. Ivory Coast in `CI`, Japan in `JP`) — either from real geo data or as explicit fallback.
- [ ] **Regional fallback:** CONMEBOL teams weighted in South America, UEFA in Europe, CAF in Africa, etc., using confederation from `teams.py` when local data is thin.
- [ ] **Global fallback:** Worldwide Trends top teams only for countries with no regional signal — not the same 2–3 teams everywhere.
- [ ] **Variation:** Scores must differ by country; remove single global base + hash pattern.

#### 4) Copy / UX

- [ ] Rename hover header: **“Search interest in FIFA participating nations”** (not “Top 5 supported teams”).
- [ ] Update subtitle: e.g. “Google Trends · which WC nation is searched most in each country”.
- [ ] **Methodology hover** on section: per-country Trends queries, home-country rule, regional fallback, data refresh cadence (daily).
- [ ] Dropdown: all **48** teams (use `WC_TEAMS`), not `HIGHLIGHT_TEAMS` (9 only).

#### 5) Backend / infra notes

- [ ] Rate limits: per-country Trends needs batching (5 queries/request, delays) — may need subset of countries per daily run or rotate geos across days.
- [ ] Consider caching latest geo snapshot per country in DB; API reads last run only.

### Open questions for implementation

- Which countries to query every day vs rotate (all UN members vs ~80 strategic geos).
- Exact home-country boost: hard #1 vs score multiplier.
- Whether to show interest **intensity** (choropleth colour) in addition to top-team flag pin.

---

## 4) Topic Clusters (Bluesky)

### What it should do

- Group Bluesky discussion into themes: Injuries, Goals, VAR, Tactics, Fan banter, Squad.
- Bubble size = keyword volume per cluster from real posts.
- Right panel = **real top posts** from Bluesky for that cluster.

### Root cause — same tweet everywhere, blank bubbles

| Issue | Cause |
|-------|--------|
| **Identical “Top posts”** | `/api/clusters` **does not use Bluesky posts**. It injects **hardcoded templates** per cluster (`sample_posts` dict) with fake handle `fanpulse.bsky.social` and fake reach `120 + i*30`. Same text repeated 5×; only `{team}` changes (defaults to **Argentina**). |
| **Blank clusters (0)** | Volumes come from `keyword_snapshots` keywords matched to `topics.CLUSTERS`. Many keywords don’t match cluster rules → **General** (skipped). Goals / Referee / Fan / Squad often have **no matching keywords** in current data. |
| **Wrong keyword source** | Cluster API reads **all** `keyword_snapshots` (no `source = 'bluesky'` filter) — may mix Google Trends buzzwords into cluster volumes. |
| **Team filter** | Filtering by team only keeps keywords where `team_association == team` — can zero out most clusters. |

### Changes to implement (confirmed)

- [ ] **Store real posts per cluster** during Bluesky collection (post text, handle, uri, reach, team, cluster from `assign_cluster(post text)`).
- [ ] **API:** return top N **distinct real posts** per cluster from DB — **delete** `sample_posts` / `fanpulse.bsky.social` placeholders entirely.
- [ ] Filter keywords for cluster volume: `source = 'bluesky'` only.
- [ ] Dedupe posts by URI/text; don’t repeat the same tweet 5 times.
- [ ] Show **top keywords** per cluster (already partially there) when posts sparse.
- [ ] **Dropdown UI fix:** dark background on `<select>` **and** `<option>` elements (`bg-[#1a1a22] text-white`) — native OS dropdown shows white list with invisible white text (see screenshot). Match `GeographicHeatmap` select styling.
- [ ] Remove dead `ALL_TEAMS` constant in `TopicClusters.tsx` if still present.

---

## 5) Influencer Tracker (Bluesky)

### What it does today

- Ranks top 20 Bluesky **handles** by `reach_score` (likes + reposts on posts found via WC team searches).
- Saves **real post text** in `viral_post` from highest-reach post per handle (`bluesky.py` → `influencer_snapshots`).
- Tabs: All / Amplifiers (sentiment > 0.25) / Critics (< −0.25).

### Are these real tweets?

**Mixed — depends on collection mode:**

| Mode | Tweets |
|------|--------|
| **LIVE** (Bluesky credentials + search works) | **Real posts** from API — e.g. `@rgomezs2000.bsky.social`, `@firsttouch.bsky.social` in screenshot are genuine captured text. |
| **DEMO fallback** (`BLUESKY_DEMO_FALLBACK=true` or dev default) | **Synthetic** posts from `DEMO_TEMPLATES`, handles like `fan{N}.bsky.social` — not real users. |

**Caveats even when LIVE:**

- Not “top football influencers” — anyone who posted matching `"{Team} WorldCup2026"` / `"{Team} FIFA2026"` with high likes.
- Includes **bots/off-topic** (e.g. trending-words bot about Ukraine/Iran in screenshot).
- Reach = likes + reposts on **one search window**, not follower count.
- Many real WC voices (journalists, players) may **not** be on Bluesky → section may have limited value.

### User decision (confirmed direction)

- **Prefer real tweets only** — no demo/synthetic influencers in production (`BLUESKY_DEMO_FALLBACK=false` on GitHub Actions).
- **If live data too noisy or thin:** consider **removing Influencer Tracker section** rather than showing non-football accounts.
- Alternative (if kept): rename to **“Accounts discussing WC teams”**, filter posts must match cluster keywords / football filter, hide handles with non-football viral text.

### Changes to implement (options — pick at build time)

**Option A — Fix & keep**

- [ ] LIVE-only gate: hide section or show empty state when `BLUESKY_DEMO_FALLBACK` or no `influencer_snapshots` from live run.
- [ ] Filter influencers: `is_football_keyword` / cluster match on `viral_post`; exclude bot patterns.
- [ ] Link to real Bluesky post URL if URI stored (future).
- [ ] Clarify metric: “reach = likes + reposts on WC-related posts”.

**Option B — Remove section**

- [ ] Remove `InfluencerTracker` from `Analytics.tsx` and nav subtitle.
- [ ] Stop collecting `influencer_snapshots` (optional cleanup).

**UI (if kept):** no dropdown in this section currently; tab buttons are fine.

---

## 6) (pending — user will discuss next)
