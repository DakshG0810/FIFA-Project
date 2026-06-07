import { useState, useCallback, useMemo } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import SentimentBar from "../components/SentimentBar"
import LoadingSkeleton from "../components/LoadingSkeleton"
import DataBadge from "../components/DataBadge"
import { useDataMode } from "../hooks/useDataMode"
import { getFlagImageUrl } from "../data/teamFlagCodes"
import TopicClusters from "../components/TopicClusters"
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

type SortMode = "mentions" | "most_positive" | "most_negative" | "positive_pct"

const OVERALL_SCORE_CALC =
  "Each Bluesky post is analyzed for tone, averaged per collection run, then averaged across all runs for that team."

const SORT_TABS: {
  key: SortMode
  label: string
  title: string
  detail: string
  calculation?: string
}[] = [
  {
    key: "mentions",
    label: "Most discussed",
    title: "Most discussed",
    detail: "Ranked by total Bluesky posts across every collection run.",
  },
  {
    key: "most_positive",
    label: "Most positive",
    title: "Most positive overall",
    detail: "Highest overall fan sentiment score on −1 to +1 scale. +1 = very positive tone.",
    calculation: OVERALL_SCORE_CALC,
  },
  {
    key: "most_negative",
    label: "Most negative",
    title: "Most negative overall",
    detail: "Lowest overall fan sentiment score on −1 to +1 scale. −1 = very negative tone.",
    calculation: OVERALL_SCORE_CALC,
  },
  {
    key: "positive_pct",
    label: "Highest positive %",
    title: "Highest positive word %",
    detail: "Ranked by what % of post words are positive — a different measure from the overall score above.",
  },
]

function TeamFlagImg({ team, size = 20 }: { team: string; size?: number }) {
  const src = getFlagImageUrl(team, "sm")
  if (!src) return null
  return (
    <img
      src={src}
      alt=""
      width={Math.round(size * 1.35)}
      height={size}
      className="rounded-sm border border-white/15 object-cover shrink-0"
    />
  )
}

function formatChartDay(isoDate: string) {
  const d = new Date(isoDate.includes("T") ? isoDate : `${isoDate}T12:00:00`)
  if (Number.isNaN(d.getTime())) return isoDate
  return d.toLocaleDateString("en", { month: "short", day: "numeric" })
}

function sortTeams(rows: SentimentRow[], mode: SortMode) {
  const copy = [...rows]
  switch (mode) {
    case "most_positive":
      return copy.sort((a, b) => (b.compound || 0) - (a.compound || 0))
    case "most_negative":
      return copy.sort((a, b) => (a.compound || 0) - (b.compound || 0))
    case "positive_pct":
      return copy.sort((a, b) => (b.positive || 0) - (a.positive || 0))
    default:
      return copy.sort((a, b) => (b.mentions || 0) - (a.mentions || 0))
  }
}

export default function Sentiment() {
  const badge = useDataMode("bluesky")
  const [sort, setSort] = useState<SortMode>("mentions")
  const [selected, setSelected] = useState<string | null>(null)

  const fetchSentiment = useCallback(() => api.sentiment(0, "bluesky"), [])
  const fetchHistory = useCallback(() => {
    if (!selected) return Promise.resolve([])
    return api.teamHistory(selected, "bluesky")
  }, [selected])

  const { data, loading } = useApi<SentimentRow[]>(fetchSentiment, [], 60000)
  const { data: history, loading: histLoading } = useApi(fetchHistory, [], 120000)

  const sorted = useMemo(() => sortTeams(data, sort), [data, sort])

  const chartData = useMemo(
    () =>
      history.map((h) => ({
        time: formatChartDay(h.captured_at),
        compound: parseFloat((h.compound || 0).toFixed(3)),
        mentions: h.mentions || 0,
      })),
    [history]
  )

  return (
    <div className="space-y-6 w-full max-w-full">
      <div className="flex items-center gap-2">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Buzz</h1>
          <p className="text-white/40 text-sm">
            Fan sentiment & discussion from Bluesky · topic clusters
          </p>
        </div>
        <DataBadge mode={badge} />
      </div>

      <div className="flex gap-2 flex-wrap">
        {SORT_TABS.map((tab) => (
          <div key={tab.key} className="relative group">
            <button
              type="button"
              onClick={() => setSort(tab.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                sort === tab.key
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-white/5 text-white/50 border border-white/10 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
            <div
              role="tooltip"
              className="pointer-events-none absolute left-0 top-full z-20 mt-2 w-56 rounded-lg border border-white/15 bg-[#0a0a0e] px-3 py-2 text-[11px] text-white/80 opacity-0 shadow-xl transition-opacity group-hover:opacity-100"
            >
              <p className="font-medium text-white mb-1">{tab.title}</p>
              <p>{tab.detail}</p>
              {tab.calculation ? (
                <p className="text-white/50 mt-1">{tab.calculation}</p>
              ) : null}
            </div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-5 gap-4">
        <div className="md:col-span-3 space-y-1.5">
          {loading ? (
            <LoadingSkeleton rows={10} />
          ) : (
            <>
              <div className="hidden sm:flex items-center gap-3 px-4 py-2 text-[10px] uppercase tracking-wider text-white/35 border-b border-white/10">
                <span className="w-7 shrink-0" aria-hidden />
                <span className="w-28 shrink-0">Team</span>
                <span className="flex-1">Tone</span>
                <span className="w-16 text-right shrink-0">Posts</span>
                <span className="w-14 text-right shrink-0">Score</span>
              </div>
              {sorted.map((team) => {
                const pos = Math.round((team.positive || 0) * 100)
                const neg = Math.round((team.negative || 0) * 100)
                const comp = team.compound || 0
                return (
                  <button
                    key={team.team}
                    type="button"
                    onClick={() => setSelected(selected === team.team ? null : team.team)}
                    className={`w-full flex items-center gap-3 rounded-xl px-4 py-3 border transition-all text-left ${
                      selected === team.team
                        ? "bg-emerald-500/10 border-emerald-500/30"
                        : "bg-white/5 border-white/5 hover:bg-white/8 hover:border-white/10"
                    }`}
                  >
                    <TeamFlagImg team={team.team} size={18} />
                    <span className="text-white text-sm font-medium w-28 shrink-0">{team.team}</span>
                    <div className="flex-1 min-w-0">
                      <SentimentBar positive={team.positive} negative={team.negative} size="sm" />
                      <div className="flex gap-3 mt-1">
                        <span className="text-emerald-400 text-xs">{pos}% pos words</span>
                        <span className="text-red-400 text-xs">{neg}% neg words</span>
                      </div>
                    </div>
                    <span className="text-white text-xs font-mono w-16 text-right shrink-0">
                      {(team.mentions || 0).toLocaleString()}
                    </span>
                    <span
                      className={`text-xs font-mono w-14 text-right shrink-0 ${
                        comp >= 0.1 ? "text-emerald-400" : comp <= -0.1 ? "text-red-400" : "text-white/70"
                      }`}
                    >
                      {comp >= 0 ? "+" : ""}
                      {comp.toFixed(2)}
                    </span>
                  </button>
                )
              })}
            </>
          )}
        </div>

        <div className="md:col-span-2">
          {selected ? (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 sticky top-20 space-y-4">
              <div className="flex items-center gap-2">
                <TeamFlagImg team={selected} size={24} />
                <span className="text-white font-bold text-lg">{selected}</span>
              </div>
              <p className="text-white/30 text-xs">Overall sentiment score by collection day</p>
              {histLoading ? (
                <div className="h-40 bg-white/5 rounded-lg animate-pulse" />
              ) : chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={chartData}>
                    <XAxis dataKey="time" tick={{ fill: "#ffffff50", fontSize: 10 }} />
                    <YAxis domain={[-1, 1]} tick={{ fill: "#ffffff50", fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ background: "#111", border: "1px solid #333", borderRadius: 8 }}
                      labelStyle={{ color: "#fff" }}
                      itemStyle={{ color: "#fff" }}
                    />
                    <ReferenceLine y={0} stroke="#ffffff20" strokeDasharray="3 3" />
                    <Line
                      type="monotone"
                      dataKey="compound"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ r: 3, fill: "#10b981" }}
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
              <span className="text-white/20 text-sm">Select a team to view history</span>
            </div>
          )}
        </div>
      </div>

      <TopicClusters />
    </div>
  )
}
