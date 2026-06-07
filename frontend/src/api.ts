import type {
  ApiStatus,
  BuzzTeam,
  CountryTrend,
  HistoryPoint,
  Influencer,
  Keyword,
  InterestOddsData,
  NarrativePoint,
  OddsEntry,
  SentimentRow,
  SpikeAlert,
  SpikeHeatmapData,
  TeamSentiment,
  TopicCluster,
  TrendsEntry,
} from "./types"

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function get<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${BASE}${path}`)
    if (!res.ok) {
      console.warn(`[API] ${path} → HTTP ${res.status}`)
      throw new Error(`HTTP ${res.status}`)
    }
    return res.json() as Promise<T>
  } catch (e) {
    console.warn(`[API] ${path} failed`, e)
    return fallback
  }
}

export const api = {
  status: () => get<ApiStatus>("/api/status", { status: "offline", total_snapshots: 0, server_time: "" }),
  leaderboard: () => get<TeamSentiment[]>("/api/leaderboard", []),
  sentiment: (hours = 24, source?: string) =>
    get<SentimentRow[]>(
      `/api/sentiment?hours=${hours}${source ? `&source=${encodeURIComponent(source)}` : ""}`,
      []
    ),
  teamHistory: (team: string, source = "bluesky") =>
    get<HistoryPoint[]>(
      `/api/sentiment/${encodeURIComponent(team)}/history?source=${encodeURIComponent(source)}`,
      []
    ),
  odds: () => get<OddsEntry[]>("/api/odds", []),
  oddsHistory: (team: string) =>
    get<{ captured_at: string; win_probability: number; decimal_odds: number }[]>(
      `/api/odds/${encodeURIComponent(team)}/history`,
      []
    ),
  trends: () => get<TrendsEntry[]>("/api/trends", []),
  keywords: (limit = 80, category?: string, source?: string, hours = 168) =>
    get<Keyword[]>(
      `/api/keywords?limit=${limit}&hours=${hours}${
        category && category !== "all" ? `&category=${encodeURIComponent(category)}` : ""
      }${source ? `&source=${encodeURIComponent(source)}` : ""}`,
      []
    ),
  spikes: () => get<SpikeAlert[]>("/api/spikes", []),
  buzz: () => get<BuzzTeam[]>("/api/buzz", []),
  spikeHeatmap: () => get<SpikeHeatmapData>("/api/spikes/heatmap", { teams: [], buckets: 0, dates: [], cells: [], max_mentions: 1 }),
  clusters: (team?: string) =>
    get<{ clusters: TopicCluster[]; team_filter: string | null }>(
      `/api/clusters${team ? `?team=${encodeURIComponent(team)}` : ""}`,
      { clusters: [], team_filter: null }
    ),
  influencers: (tab = "all") =>
    get<Influencer[]>(`/api/influencers?tab=${tab}`, []),
  trendRegions: (team?: string) =>
    get<{ countries: CountryTrend[]; highlight_team: string | null }>(
      `/api/trends/regions${team ? `?team=${encodeURIComponent(team)}` : ""}`,
      { countries: [], highlight_team: null }
    ),
  narrative: (teams: string[]) =>
    get<{ teams: string[]; points: NarrativePoint[]; first_collection_date?: string | null }>(
      `/api/narrative?teams=${teams.map(encodeURIComponent).join(",")}`,
      { teams: [], points: [] }
    ),
  interestOdds: () =>
    get<InterestOddsData>("/api/interest-odds", {
      convergence: [],
      higher_odds_lower_interest: [],
      higher_interest_lower_odds: [],
    }),
}
