import { useState, useCallback, useMemo } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { OddsEntry, TeamSentiment } from "../types"
import TeamFlag from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import DataBadge from "../components/DataBadge"
import { useDataMode } from "../hooks/useDataMode"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

export default function Odds() {
  const badge = useDataMode("odds")
  const [selected, setSelected] = useState<string | null>(null)

  const fetchOdds = useCallback(() => api.odds(), [])
  const fetchLeaderboard = useCallback(() => api.leaderboard(), [])
  const fetchHistory = useCallback(() => {
    if (!selected) return Promise.resolve([])
    return api.oddsHistory(selected)
  }, [selected])

  const { data: odds, loading } = useApi<OddsEntry[]>(fetchOdds, [], 3600000)
  const { data: leaderboard } = useApi<TeamSentiment[]>(fetchLeaderboard, [], 120000)
  const { data: history } = useApi(fetchHistory, [], 3600000)

  const divergenceMap = useMemo(() => {
    const sentRank = [...leaderboard]
      .sort((a, b) => (b.compound || 0) - (a.compound || 0))
      .map((t, i) => ({ team: t.team, rank: i + 1 }))
    const oddsRank = [...odds]
      .sort((a, b) => (b.win_probability || 0) - (a.win_probability || 0))
      .map((t, i) => ({ team: t.team, rank: i + 1 }))
    const m = new Map<string, number>()
    for (const s of sentRank) {
      const o = oddsRank.find((x) => x.team === s.team)
      if (o) m.set(s.team, o.rank - s.rank)
    }
    return m
  }, [leaderboard, odds])

  const sorted = [...odds].sort((a, b) => (b.win_probability || 0) - (a.win_probability || 0))
  const top3 = sorted.slice(0, 3)
  const rest = sorted.slice(3)

  const chartData = history.map((h) => ({
    time: new Date(h.captured_at).toLocaleDateString("en", { month: "short", day: "numeric" }),
    prob: parseFloat(((h.win_probability || 0) * 100).toFixed(2)),
  }))

  const probDelta = history.length >= 2
    ? (history[history.length - 1].win_probability - history[0].win_probability) * 100
    : 0

  const podiumColors = [
    "border-amber-400/40 bg-amber-400/10",
    "border-white/20 bg-white/5",
    "border-orange-600/40 bg-orange-600/10",
  ]
  const podiumLabels = ["🥇", "🥈", "🥉"]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Live Odds Tracker</h1>
          <p className="text-white/40 text-sm">Win probabilities from bookmakers</p>
        </div>
        <DataBadge mode={badge} />
      </div>

      {loading ? (
        <LoadingSkeleton rows={6} />
      ) : odds.length === 0 ? (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-12 text-center">
          <p className="text-white/40">No odds data available yet</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-3">
            {top3.map((team, i) => (
              <button
                key={team.team}
                onClick={() => setSelected(selected === team.team ? null : team.team)}
                className={`rounded-2xl border p-4 text-center transition-all ${podiumColors[i]} ${
                  selected === team.team ? "ring-1 ring-white/20" : "hover:brightness-125"
                }`}
              >
                <div className="text-2xl mb-1">{podiumLabels[i]}</div>
                <TeamFlag team={team.team} size="lg" />
                <div className="text-white font-bold text-sm mt-2">{team.team}</div>
                <div className="text-emerald-400 text-xl font-black mt-1 font-mono">
                  {((team.win_probability || 0) * 100).toFixed(1)}%
                </div>
                <div className="text-white/30 text-xs">win probability</div>
              </button>
            ))}
          </div>

          <div className="space-y-1.5">
            {rest.map((team, i) => {
              const delta = divergenceMap.get(team.team) ?? 0
              const flash = Math.abs(delta) > 5
              return (
                <button
                  key={team.team}
                  onClick={() => setSelected(selected === team.team ? null : team.team)}
                  className={`w-full flex items-center gap-3 rounded-xl px-4 py-3 border transition-all text-left ${
                    selected === team.team ? "bg-emerald-500/10 border-emerald-500/30" : "bg-white/5 border-white/5 hover:bg-white/8"
                  }`}
                >
                  <span className="text-white/20 text-xs w-5 text-right">{i + 4}</span>
                  <TeamFlag team={team.team} size="sm" />
                  <span className="text-white text-sm font-medium flex-1">{team.team}</span>
                  <span className="text-amber-400 font-mono text-sm w-14 text-right">
                    {((team.win_probability || 0) * 100).toFixed(1)}%
                  </span>
                  <span className="w-8 text-center text-xs" title="Sentiment vs odds rank gap">
                    {flash ? <span className="text-amber-400">⚡</span> : <span className="text-white/20">—</span>}
                  </span>
                </button>
              )
            })}
          </div>

          {selected && (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
              <div className="flex items-center gap-2 flex-wrap">
                <TeamFlag team={selected} size="sm" />
                <span className="text-white font-medium">{selected} probability history</span>
                {history.length >= 2 && (
                  <span className={`text-xs font-mono ml-auto ${probDelta >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {probDelta >= 0 ? "▲" : "▼"} {Math.abs(probDelta).toFixed(2)}% (period)
                  </span>
                )}
              </div>
              {chartData.length > 1 ? (
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={chartData}>
                    <XAxis dataKey="time" tick={{ fill: "#ffffff40", fontSize: 10 }} />
                    <YAxis tick={{ fill: "#ffffff40", fontSize: 10 }} unit="%" />
                    <Tooltip contentStyle={{ background: "#111", border: "1px solid #333" }} />
                    <Line type="monotone" dataKey="prob" stroke="#f59e0b" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-white/20 text-sm py-8 text-center">Waiting for more history…</div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
