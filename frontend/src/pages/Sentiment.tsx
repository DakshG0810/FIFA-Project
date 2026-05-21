import { useState, useCallback } from "react"

import { useApi } from "../hooks/useApi"
import { api } from "../api"

import SentimentBar from "../components/SentimentBar"
import TeamFlag from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import MomentumArrow from "../components/MomentumArrow"
import DataBadge from "../components/DataBadge"
import { useDataMode } from "../hooks/useDataMode"
import type { SentimentRow } from "../types"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"

type Sort =
  | "compound"
  | "mentions"
  | "positive"
  | "negative"

export default function Sentiment() {
  const badge = useDataMode("bluesky")

  const [sort, setSort] =
    useState<Sort>("mentions")

  const [selected, setSelected] =
    useState<string | null>(null)

  // SAFE FETCHERS

  const fetchSentiment = useCallback(
    () => api.sentiment(48, "bluesky"),
    []
  )

  const fetchHistory = useCallback(() => {

    if (!selected) {
      return Promise.resolve([])
    }

    return api.teamHistory(selected)

  }, [selected])

  // SAFE API HOOKS

  const { data, loading } = useApi<SentimentRow[]>(fetchSentiment, [], 60000)

  const {
    data: history,
    loading: histLoading,
  } = useApi(fetchHistory, [], 120000)

  // SORTING

  const sorted = [...data].sort(
    (a: any, b: any) => {

      if (sort === "compound") {
        return (b.compound || 0) -
               (a.compound || 0)
      }

      if (sort === "positive") {
        return (b.positive || 0) -
               (a.positive || 0)
      }

      if (sort === "negative") {
        return (b.negative || 0) -
               (a.negative || 0)
      }

      return (b.mentions || 0) -
             (a.mentions || 0)
    }
  )

  // CHART DATA

  const chartData = history.map((h: any) => ({
    time: new Date(h.captured_at).toLocaleDateString(
      "en",
      {
        month: "short",
        day: "numeric",
        hour: "2-digit",
      }
    ),
    compound: parseFloat(
      (h.compound || 0).toFixed(3)
    ),
    mentions: h.mentions || 0,
  }))

  const sortButtons = [
    {
      key: "mentions",
      label: "Most discussed",
    },
    {
      key: "compound",
      label: "Most positive",
    },
    {
      key: "negative",
      label: "Most negative",
    },
    {
      key: "positive",
      label: "Highest positive %",
    },
  ]

  return (
    <div className="space-y-6">

      <div className="flex items-center gap-2">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Sentiment Leaderboard</h1>
          <p className="text-white/40 text-sm">Fan sentiment from Bluesky posts</p>
        </div>
        <DataBadge mode={badge} />
      </div>

      {/* SORT BUTTONS */}

      <div className="flex gap-2 flex-wrap">

        {sortButtons.map((b: any) => (

          <button
            key={b.key}
            onClick={() => setSort(b.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              sort === b.key
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                : "bg-white/5 text-white/50 border border-white/10 hover:text-white"
            }`}
          >

            {b.label}

          </button>

        ))}

      </div>

      <div className="grid md:grid-cols-5 gap-4">

        {/* TEAM LIST */}

        <div className="md:col-span-3 space-y-1.5">

          {loading ? (

            <LoadingSkeleton rows={10} />

          ) : (

            sorted.map((team: any) => {

              const pos = Math.round(
                (team.positive || 0) * 100
              )

              const neg = Math.round(
                (team.negative || 0) * 100
              )

              const comp =
                team.compound || 0

              return (

                <button
                  key={team.team}
                  onClick={() =>
                    setSelected(
                      selected === team.team
                        ? null
                        : team.team
                    )
                  }
                  className={`w-full flex items-center gap-3 rounded-xl px-4 py-3 border transition-all text-left ${
                    selected === team.team
                      ? "bg-emerald-500/10 border-emerald-500/30"
                      : "bg-white/5 border-white/5 hover:bg-white/8 hover:border-white/10"
                  }`}
                >

                  <TeamFlag
                    team={team.team}
                    size="sm"
                  />

                  <span className="text-white text-sm font-medium w-28 shrink-0">
                    {team.team}
                  </span>

                  <div className="flex-1 min-w-0">

                    <SentimentBar
                      positive={team.positive}
                      negative={team.negative}
                      size="sm"
                    />

                    <div className="flex gap-3 mt-1">

                      <span className="text-emerald-400 text-xs">
                        {pos}% pos
                      </span>

                      <span className="text-red-400 text-xs">
                        {neg}% neg
                      </span>

                    </div>

                  </div>

                  <MomentumArrow momentum={comp >= 0.05 ? "up" : comp <= -0.05 ? "down" : "flat"} />
                  <span
                    className={`text-xs font-mono shrink-0 ${
                      comp >= 0.1 ? "text-emerald-400" : comp <= -0.1 ? "text-red-400" : "text-white/30"
                    }`}
                  >
                    {comp >= 0 ? "+" : ""}{comp.toFixed(3)}
                  </span>

                </button>

              )
            })

          )}

        </div>

        {/* DETAIL PANEL */}

        <div className="md:col-span-2">

          {selected ? (

            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 sticky top-20 space-y-4">

              <div className="flex items-center gap-2">

                <TeamFlag
                  team={selected}
                  size="md"
                />

                <span className="text-white font-bold text-lg">
                  {selected}
                </span>

              </div>

              <p className="text-white/30 text-xs">
                Sentiment over time
              </p>

              {histLoading ? (

                <div className="h-40 bg-white/5 rounded-lg animate-pulse" />

              ) : chartData.length > 0 ? (

                <ResponsiveContainer
                  width="100%"
                  height={160}
                >

                  <LineChart data={chartData}>

                    <XAxis
                      dataKey="time"
                      tick={{
                        fill: "#ffffff30",
                        fontSize: 10,
                      }}
                    />

                    <YAxis
                      domain={[-1, 1]}
                      tick={{
                        fill: "#ffffff30",
                        fontSize: 10,
                      }}
                    />

                    <Tooltip />

                    <ReferenceLine
                      y={0}
                      stroke="#ffffff20"
                      strokeDasharray="3 3"
                    />

                    <Line
                      type="monotone"
                      dataKey="compound"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={false}
                    />

                  </LineChart>

                </ResponsiveContainer>

              ) : (

                <div className="h-40 flex items-center justify-center text-white/20 text-sm">
                  No history available yet
                </div>

              )}

            </div>

          ) : (

            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center justify-center h-40">

              <span className="text-white/20 text-sm">
                Select a team to view history
              </span>

            </div>

          )}

        </div>

      </div>

    </div>
  )
}