export interface TeamSentiment {
  team: string
  compound: number
  positive: number
  negative: number
  mentions: number
  reach: number
  win_probability?: number
  trends_score?: number
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
  team: string
  source: string
  mentions_current: number
  mentions_average: number
  spike_multiplier: number
  inferred_trigger: string
  detected_at: string
}

export interface ApiStatus {
  status: string
  last_bluesky?: string
  last_google_trends?: string
  last_odds?: string
  total_snapshots: number
  server_time: string
}

export interface HistoryPoint {
  captured_at: string
  compound: number
  mentions: number
  source?: string
}
