# Overview page — changes log

## Team Buzz Volume
- White tooltip text for mentions
- Confederation colour legend (UEFA, CONMEBOL, CONCACAF, AFC, CAF, OFC)
- Relative buzz hover: `current mentions ÷ 6h rolling average`
- All 32 teams on y-axis (no height cap)
- Sparkline detail list removed

## Mention Heatmap
- X-axis: **collection day** (not 24h half-hour buckets)
- Range: first Bluesky snapshot → latest
- Tooltip: team · date · post count

## Team Leaderboard
- Header row: #, Team, Confed., Tone, **Posts**, **Win %**, **Δ**, **Sentiment**
- **Posts**: `SUM(mention_count)` across **all** Bluesky collection runs (not last 48h)
- **Win %**: bookmaker implied win probability (Odds API, latest run)
- **Δ**: momentum arrow — sentiment compound first collection vs latest
- **Sentiment**: average VADER compound (−1 to +1) across all runs
