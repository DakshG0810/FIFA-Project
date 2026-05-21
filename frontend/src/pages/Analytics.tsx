import { useState, useCallback } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"

import TeamFlag, { getFlag } from "../components/TeamFlag"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from "recharts"

const TEAM_COLORS = [
  "#10b981",
  "#3b82f6",
  "#f59e0b",
  "#ef4444",
]

const ALL_TEAMS = [
  "Argentina",
  "France",
  "England",
  "Brazil",
  "Spain",
  "Germany",
  "Portugal",
  "Netherlands",
]

export default function Analytics() {

  const [selected, setSelected] = useState([
    "Argentina",
    "France",
    "England",
    "Brazil",
  ])

  // SAFE API HOOKS

  const fetchLeaderboard = useCallback(
    () => api.leaderboard(),
    []
  )

  const fetchOdds = useCallback(
    () => api.odds(),
    []
  )

  const {
    data: leaderboard,
  } = useApi(fetchLeaderboard, [], 120000)

  const {
    data: odds,
  } = useApi(fetchOdds, [], 120000)

  // TEMP MOCK CHART DATA

  const chartData = [
    {
      time: "10:00",
      Argentina: 0.3,
      France: 0.2,
      England: 0.1,
      Brazil: 0.4,
    },
    {
      time: "11:00",
      Argentina: 0.5,
      France: 0.1,
      England: 0.2,
      Brazil: 0.6,
    },
    {
      time: "12:00",
      Argentina: 0.7,
      France: 0.3,
      England: 0.25,
      Brazil: 0.5,
    },
  ]

  const toggleTeam = (team: string) => {
    setSelected((prev) => {
      if (prev.includes(team)) {
        return prev.filter((t) => t !== team)
      }

      if (prev.length >= 4) {
        return prev
      }

      return [...prev, team]
    })
  }

  const sentimentRanked = [...leaderboard]
    .sort((a: any, b: any) => (b.compound || 0) - (a.compound || 0))
    .map((t: any, i) => ({
      team: t.team,
      sentimentRank: i + 1,
    }))

  const oddsRanked = [...odds]
    .sort((a: any, b: any) => (b.win_probability || 0) - (a.win_probability || 0))
    .map((t: any, i) => ({
      team: t.team,
      oddsRank: i + 1,
    }))

  const divergence = sentimentRanked
    .map((s) => {
      const o = oddsRanked.find((x) => x.team === s.team)

      if (!o) return null

      return {
        team: s.team,
        sentimentRank: s.sentimentRank,
        oddsRank: o.oddsRank,
        delta: o.oddsRank - s.sentimentRank,
      }
    })
    .filter(Boolean)
    .sort((a: any, b: any) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 10)

  return (
    <div className="space-y-8">

      <div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Analytics
        </h1>

        <p className="text-white/40 text-sm">
          Narrative shift · Sentiment vs odds divergence
        </p>
      </div>

      {/* TEAM SELECTOR */}

      <div className="flex flex-wrap gap-2">
        {ALL_TEAMS.map((team) => {
          const isSelected = selected.includes(team)
          const colorIndex = selected.indexOf(team)

          return (
            <button
              key={team}
              onClick={() => toggleTeam(team)}
              className={`px-3 py-1.5 rounded-full text-xs border transition-all ${
                isSelected
                  ? "text-black border-transparent"
                  : "bg-white/5 border-white/10 text-white/60"
              }`}
              style={
                isSelected
                  ? { background: TEAM_COLORS[colorIndex] }
                  : {}
              }
            >
              {getFlag(team)} {team}
            </button>
          )
        })}
      </div>

      {/* CHART */}

      <div className="bg-white/5 border border-white/10 rounded-2xl p-5">

        <h2 className="text-white font-semibold mb-4">
          Sentiment Movement
        </h2>

        <ResponsiveContainer width="100%" height={300}>

          <LineChart data={chartData}>

            <XAxis
              dataKey="time"
              tick={{ fill: "#ffffff40", fontSize: 10 }}
            />

            <YAxis
              domain={[-1, 1]}
              tick={{ fill: "#ffffff40", fontSize: 10 }}
            />

            <Tooltip />

            <Legend />

            <ReferenceLine
              y={0}
              stroke="#ffffff20"
              strokeDasharray="3 3"
            />

            {selected.map((team, i) => (
              <Line
                key={team}
                type="monotone"
                dataKey={team}
                stroke={TEAM_COLORS[i]}
                strokeWidth={2}
                dot={false}
              />
            ))}

          </LineChart>

        </ResponsiveContainer>

      </div>

      {/* DIVERGENCE */}

      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">

        <div>
          <h2 className="text-white font-semibold mb-1">
            Sentiment vs Odds Divergence
          </h2>

          <p className="text-white/40 text-xs">
            Teams where public sentiment differs from betting markets
          </p>
        </div>

        {divergence.length === 0 ? (

          <div className="text-white/20 text-sm py-8 text-center">
            Waiting for live data...
          </div>

        ) : (

          <div className="space-y-2">

            {divergence.map((d: any) => {

              const fansHigher = d.delta > 0

              return (
                <div
                  key={d.team}
                  className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 flex items-center gap-3"
                >

                  <TeamFlag team={d.team} size="sm" />

                  <div className="flex-1">

                    <div className="text-white text-sm font-medium">
                      {d.team}
                    </div>

                    <div className="text-white/40 text-xs">
                      Sentiment #{d.sentimentRank} · Odds #{d.oddsRank}
                    </div>

                  </div>

                  <span
                    className={`text-xs px-2 py-1 rounded-lg ${
                      fansHigher
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {fansHigher
                      ? "Fans more optimistic"
                      : "Bookmakers more optimistic"}
                  </span>

                </div>
              )
            })}

          </div>

        )}

      </div>

    </div>
  )
}