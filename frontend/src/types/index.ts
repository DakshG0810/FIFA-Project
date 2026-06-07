export interface TeamSentiment {
  team: string
  compound: number
  positive: number
  negative: number
  mentions: number
  reach: number
  win_probability?: number | null
  trends_score?: number | null
  momentum?: "up" | "down" | "flat"
}

export interface SentimentRow {
  team: string
  positive: number
  negative: number
  compound: number
  mentions: number
  total_reach: number
}

export interface OddsEntry {
  team: string
  win_probability: number
  decimal_odds: number
  bookmaker: string
  captured_at: string
}

export interface TrendsEntry {
  team: string
  interest_score: number
  region: string
  captured_at: string
}

export interface Keyword {
  keyword: string
  total_freq: number
  team_association?: string
}

export interface SpikeAlert {
  id?: number
  team: string
  source: string
  mentions_current: number
  mentions_average: number
  spike_multiplier: number
  inferred_trigger: string
  detected_at: string
}

export type DataMode = "LIVE" | "CACHED" | "DEMO"

export interface ApiStatus {
  status: string
  last_bluesky?: string
  last_google_trends?: string
  last_odds?: string
  total_snapshots: number
  server_time: string
  data_sources?: {
    bluesky?: string
    google_trends?: string
    odds?: string
  }
  collection_schedule?: {
    bluesky_minutes: number
    odds_minutes: number
    trends_hours: number
  }
}

export interface HistoryPoint {
  captured_at: string
  compound: number
  mentions: number
  source?: string
}

export interface BuzzTeam {
  team: string
  mentions: number
  rolling_avg_6h: number
  relative_multiplier: number
  sparkline: number[]
  confederation: string
  confederation_color: string
}

export interface SpikeHeatmapData {
  teams: string[]
  buckets: number
  dates?: string[]
  first_collection_date?: string | null
  last_collection_date?: string | null
  cells: { team: string; bucket: number; mentions: number; intensity: number }[]
  max_mentions: number
}

export interface TopicCluster {
  id: string
  name: string
  icon: string
  volume: number
  top_keywords: { keyword: string; freq: number }[]
  top_posts: { text: string; handle: string; reach: number }[]
}

export interface Influencer {
  handle: string
  display_name: string
  reach_score: number
  primary_team: string
  sentiment: number
  viral_post: string
  captured_at?: string
}

export interface CountryTrend {
  code: string
  name: string
  has_regional_data?: boolean
  top_team: string | null
  top3: { team: string; score: number }[]
  top5: { team: string; score: number }[]
  highlight_score: number
}

export interface NarrativePoint {
  time: string
  [key: string]: string | number
}

export interface InterestOddsRow {
  team: string
  odds_rank: number
  interest_rank: number
  trends_rank: number
  mentions_rank: number
  win_probability: number
  trends_score: number
  mentions: number
  gap: number
}

export interface InterestOddsData {
  convergence: InterestOddsRow[]
  higher_odds_lower_interest: InterestOddsRow[]
  higher_interest_lower_odds: InterestOddsRow[]
}
