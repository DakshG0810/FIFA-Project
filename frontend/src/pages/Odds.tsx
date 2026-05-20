import { useState } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import TeamFlag from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts"

export default function Odds() {
  const { data: odds, loading } = useApi(() => api.odds(), [], 3_600_000)
  const [selected, setSelected] = useState<string | null>(null)
  const { data: history } = useApi(
    () => selected ? api.oddsHistory(selected) : Promise.resolve([]),
    [],
    3_600_000
  )

  const sorted = [...odds].sort((a: any, b: any) => (b.win_probability || 0) - (a.win_probability || 0))
  const top3   = sorted.slice(0, 3)
  const rest   = sorted.slice(3)

  const chartData = history.map((h: any) => ({
    time: new Date(h.captured_at).toLocaleDateString("en", { month: "short", day: "numeric" }),
    prob: parseFloat(((h.win_probability || 0) * 100).toFixed(2)),
  }))

  const podiumColors = [
    "border-amber-400/40 bg-amber-400/10",
    "border-white/20 bg-white/5",
    "border-orange-600/40 bg-orange-600/10",
  ]
  const podiumLabels = ["🥇", "🥈", "🥉"]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Live odds tracker</h1>
        <p className="text-white/40 text-sm">Win probabilities from bookmakers · Cached hourly to preserve free API quota</p>
      </div>

      {loading ? (
        <LoadingSkeleton rows={6} />
      ) : odds.length === 0 ? (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-12 text-center">
          <p className="text-white/40">No odds data yet — World Cup odds may not be live until closer to the tournament</p>
          <p className="text-white/20 text-sm mt-2">The Odds API will populate this once bookmakers publish WC2026 futures</p>
        </div>
      ) : (
        <>
          {/* Top 3 podium */}
          <div className="grid grid-cols-3 gap-3">
            {top3.map((team: any, i: number) => (
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
                <div className="text-emerald-400 text-xl font-black mt-1">
                  {((team.win_probability || 0) * 100).toFixed(1)}%
                </div>
                <div className="text-white/30 text-xs">win probability</div>
              </button>
            ))}
          </div>

          {/* Full table */}
          <div className="space-y-1.5">
            {rest.map((team: any, i: number) => (
              <button
                key={team.team}
                onClick={() => setSelected(selected === team.team ? null : team.team)}
                className={`w-full flex items-center gap-3 rounded-xl px-4 py-3 border transition-all text-left ${
                  selected === team.team
                    ? "bg-emerald-500/10 border-emerald-500/30"
                    : "bg-white/5 border-white/5 hover:bg-white/8"
                }`}
              >
                <span className="text-white/20 text-xs w-5 text-right">{i + 4}</span>
                <TeamFlag team={team.team} size="sm" />
                <span className="text-white text-sm font-medium flex-1">{team.team}</span>
                <div className="w-32 bg-white/10 rounded-full h-1.5 hidden md:block">
                  <div
                    className="h-1.5 rounded-full bg-emerald-500"
                    style={{ width: `${(team.win_probability || 0) * 100 * 5}%`, maxWidth: "100%" }}
                  />
                </div>
                <span className="text-amber-400 font-mono text-sm w-14 text-right">
                  {((team.win_probability || 0) * 100).toFixed(1)}%
                </span>
                <span className="text-white/30 text-xs w-16 text-right hidden md:block">
                  {(team.decimal_odds || 0).toFixed(1)}x odds
                </span>
              </button>
            ))}
          </div>

          {/* History chart */}
          {selected && (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
              <div className="flex items-center gap-2">
                <TeamFlag team={selected} size="sm" />
                <span className="text-white font-medium">{selected} — probability over time</span>
              </div>
              {chartData.length > 1 ? (
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={chartData}>
                    <XAxis dataKey="time" tick={{ fill: "#ffffff30", fontSize: 10 }} />
                    <YAxis tick={{ fill: "#ffffff30", fontSize: 10 }} unit="%" />
                    <Tooltip
                      contentStyle={{ background: "#0a0a0a", border: "1px solid #ffffff20", borderRadius: 8 }}
                    />
                    <Line type="monotone" dataKey="prob" stroke="#f59e0b" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-white/30 text-sm py-8 text-center">
                  Not enough history yet — odds movement will appear after a few collection cycles
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
