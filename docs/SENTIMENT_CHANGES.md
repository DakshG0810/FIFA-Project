# Sentiment page — pending changes

## 1) Hover definitions on sort tabs

Add tooltips (same pattern as Overview **Relative buzz** / **Sentiment**):

| Tab | Hover text (draft) |
|-----|-------------------|
| **Most discussed** | Teams ranked by total Bluesky posts in the selected period. |
| **Most positive** | Teams ranked by overall fan sentiment score (most positive tone in posts). |
| **Most negative** | Teams ranked by share of negative wording in posts. |
| **Highest positive %** | Teams ranked by % of post text classified as positive (not the same as overall score). |

---

## 2) Remove 2-letter abbreviations (CA, US, MX…)

**Cause:** On Windows, `TeamFlag` emoji flags often render as **two-letter regional codes** (not real flag images).

**Fix:** On Sentiment page, either:
- Use **flag images** (`teamFlagCodes.ts` / flagcdn), or
- Show **team name only** (no flag component)

Do **not** show raw `CA` / `US` prefix text.

---

## 3) Sorting + show post counts

### Current bugs / gaps

| Issue | Detail |
|-------|--------|
| **No posts shown** | `mentions` exists in API but not displayed in the list |
| **48h window only** | Page calls `api.sentiment(48, "bluesky")` — not all collection runs. Leaderboard uses **all-time** sum. |
| **Most discussed** | Sort key `mentions` is correct, but data window may not match user expectation |

### Planned fix

- Change Sentiment API call to **all Bluesky snapshots** (match leaderboard aggregate), or add `hours` param = all time.
- Display **`X posts`** on each row (white text).
- Verify sort keys:

| Tab | Sort field | Meaning |
|-----|------------|---------|
| Most discussed | `mentions` (desc) | Total post count |
| Most positive | `compound` (desc) | Overall sentiment −1…+1 |
| Most negative | `negative` (desc) | Avg negative proportion 0…1 |
| Highest positive % | `positive` (desc) | Avg positive proportion 0…1 |

### Most positive vs Highest positive % — difference

| Metric | What it measures |
|--------|------------------|
| **Most positive** (`compound`) | **Overall** tone — strong negative words can pull score down even if some text is “positive” |
| **Highest positive %** (`positive`) | **% of words** tagged positive only — ignores how negative the rest is |

Example: lots of mild positive words + a few very negative sentences → high positive %, lower compound.

---

## 4) Chart — Invalid Date + similar zigzag patterns

### Invalid Date — root cause

History API returns hourly buckets like:

```text
2026-05-21T15   ← only 13 chars (date + hour)
```

Frontend does `new Date(h.captured_at)` → **Invalid Date** in JavaScript (needs full time, e.g. `T15:00:00`).

**Fix (pick one):**
- Backend: return full ISO timestamp or `YYYY-MM-DD` for daily collection, or
- Frontend: parse with `captured_at + ":00:00"` or format from date string directly

### Similar zigzag for every country — root cause

History query groups by **hour + source**:

```sql
GROUP BY substr(captured_at, 1, 13), source
```

Includes **both** `bluesky` and `google_trends` rows → two points per bucket → chart alternates → **same-looking zigzag** for every team.

**Fix:**
- Filter history to `source = 'bluesky'` only on Sentiment page, or
- Use **one point per collection day** (align with daily GitHub Action schedule)

### Chart x-axis (after fix)

For daily collection: label by **date** (May 21, Jun 6, …) not hourly buckets.

---

## Files to touch (when implementing)

| File | Changes |
|------|---------|
| `frontend/src/pages/Sentiment.tsx` | Tooltips, posts column, sorting, chart date parse, flags |
| `backend/api.py` | Optional: `sentiment` all-time param; `history` bluesky-only + daily buckets |
| `frontend/src/api.ts` | Pass `hours` or new param if needed |

---

## Status

**Notes only** — implement together when user says go (same as Overview batch).
