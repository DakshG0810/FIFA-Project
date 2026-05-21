const BASE = import.meta.env.VITE_API_URL || "http://localhost:8001"

async function get<T>(path: string): Promise<T> {
  try {
    const res = await fetch(`${BASE}${path}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  } catch {
    return [] as unknown as T
  }
}

export const api = {
  status:      ()                  => get<any>("/api/status"),
  leaderboard: ()                  => get<any[]>("/api/leaderboard"),
  sentiment:   (hours = 24)        => get<any[]>(`/api/sentiment?hours=${hours}`),
  teamHistory: (team: string)      => get<any[]>(`/api/sentiment/${encodeURIComponent(team)}/history`),
  odds:        ()                  => get<any[]>("/api/odds"),
  oddsHistory: (team: string)      => get<any[]>(`/api/odds/${encodeURIComponent(team)}/history`),
  trends:      ()                  => get<any[]>("/api/trends"),
  keywords:    (limit = 30)        => get<any[]>(`/api/keywords?limit=${limit}`),
  spikes:      ()                  => get<any[]>("/api/spikes"),
}
