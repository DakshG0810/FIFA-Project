import { useCallback } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import StatCard from "../components/StatCard"
import SentimentBar from "../components/SentimentBar"
import TeamFlag, { getFlag } from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import BuzzVolume from "../components/BuzzVolume"
import SpikeHeatmap from "../components/SpikeHeatmap"
import MomentumArrow from "../components/MomentumArrow"
import type { SpikeAlert, TeamSentiment } from "../types"

const CONF_COLORS: Record<string, string> = {
  UEFA: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  CONMEBOL: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  CONCACAF: "bg-red-500/20 text-red-300 border-red-500/30",
  AFC: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  CAF: "bg-pink-500/20 text-pink-300 border-pink-500/30",
  OFC: "bg-white/10 text-white/50 border-white/20",
}

const CONF_MAP: Record<string, string> = {
  Argentina: "CONMEBOL", France: "UEFA", England: "UEFA", Brazil: "CONMEBOL",
  Spain: "UEFA", Germany: "UEFA", Portugal: "UEFA", Netherlands: "UEFA",
  USA: "CONCACAF", Mexico: "CONCACAF", Canada: "CONCACAF", Morocco: "CAF",
  Senegal: "CAF", Japan: "AFC", "South Korea": "AFC", Australia: "AFC",
  Iran: "AFC", "Saudi Arabia": "AFC", Ecuador: "CONMEBOL", Uruguay: "CONMEBOL",
  Colombia: "CONMEBOL", Switzerland: "UEFA", Croatia: "UEFA", Serbia: "UEFA",
  Poland: "UEFA", Turkey: "UEFA", Nigeria: "CAF", Cameroon: "CAF",
  Venezuela: "CONMEBOL", Chile: "CONMEBOL", Peru: "CONMEBOL", "New Zealand": "OFC",
}

export default function Overview() {
  const fetchLeaderboard = useCallback(() => api.leaderboard(), [])
  const fetchSpikes = useCallback(() => api.spikes(), [])

  const { data: leaderboard, loading } = useApi<TeamSentiment[]>(fetchLeaderboard, [], 60000)
  const { data: spikes } = useApi<SpikeAlert[]>(fetchSpikes, [], 30000)

  const totalMentions = leaderboard.reduce((s, t) => s + (t.mentions || 0), 0)
  const avgPositivity = leaderboard.length
    ? Math.round((leaderboard.reduce((s, t) => s + (t.positive || 0), 0) / leaderboard.length) * 100)
    : 0
  const topByOdds = [...leaderboard].sort((a, b) => (b.win_probability || 0) - (a.win_probability || 0))[0]
  const fanFavourite = [...leaderboard].sort((a, b) => (b.compound || 0) - (a.compound || 0))[0]

  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-950 via-black to-black border border-emerald-500/20 p-8">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_rgba(16,185,129,0.15),transparent_60%)]" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-xs font-medium tracking-widest uppercase">Live analytics</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-2 leading-none">
            The pulse of <span className="text-emerald-400">WC 2026</span>
          </h1>
          <p className="text-white/40 text-sm max-w-xl">
            Real-time fan sentiment from Bluesky · Search buzz from Google Trends · Win probabilities from bookmakers
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total mentions" value={totalMentions.toLocaleString()} sub="across Bluesky" loading={loading} />
        <StatCard label="Avg positivity" value={`${avgPositivity}%`} sub="of all posts" accent="green" loading={loading} />
        <StatCard
          label="Bookmaker favourite"
          value={topByOdds ? `${getFlag(topByOdds.team)} ${topByOdds.team}` : "—"}
          sub={topByOdds ? `${((topByOdds.win_probability || 0) * 100).toFixed(1)}% chance` : "odds loading"}
          accent="amber"
          loading={loading}
        />
        <StatCard
          label="Fan favourite"
          value={fanFavourite ? `${getFlag(fanFavourite.team)} ${fanFavourite.team}` : "—"}
          sub="highest sentiment score"
          accent="blue"
          loading={loading}
        />
      </div>

      {spikes.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-white/50 text-xs uppercase tracking-widest">Viral spikes detected</h2>
          {spikes.slice(0, 5).map((s, i) => (
            <div
              key={s.id ?? i}
              className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3"
            >
              <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse shrink-0" />
              <TeamFlag team={s.team} size="sm" />
              <div className="flex-1 min-w-0">
                <span className="text-white text-sm font-medium">{s.team}</span>
                <p className="text-white/40 text-xs truncate">{s.inferred_trigger}</p>
              </div>
              <span className="text-red-400 text-xs font-mono shrink-0">
                +{Math.round((s.spike_multiplier - 1) * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}

      <BuzzVolume />
      <SpikeHeatmap />

      <div>
        <h2 className="text-white/50 text-xs uppercase tracking-widest mb-3">Team leaderboard</h2>
        {loading ? (
          <LoadingSkeleton rows={8} />
        ) : (
          <div className="space-y-1.5">
            {leaderboard.map((team, i) => {
              const conf = CONF_MAP[team.team] || "UEFA"
              const pct = team.win_probability ? `${(team.win_probability * 100).toFixed(1)}%` : "—"
              return (
                <div
                  key={team.team}
                  className="flex items-center gap-3 bg-white/5 hover:bg-white/8 border border-white/5 hover:border-white/10 rounded-xl px-4 py-3 transition-all"
                >
                  <span className="text-white/20 text-xs w-5 text-right shrink-0">{i + 1}</span>
                  <TeamFlag team={team.team} size="sm" />
                  <span className="text-white text-sm font-medium w-28 shrink-0">{team.team}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border hidden md:inline ${CONF_COLORS[conf]}`}>{conf}</span>
                  <div className="flex-1 min-w-0 hidden md:block">
                    <SentimentBar positive={team.positive} negative={team.negative} size="sm" />
                  </div>
                  <span className="text-white/40 text-xs w-20 text-right shrink-0">{(team.mentions || 0).toLocaleString()} posts</span>
                  <span className="text-amber-400 text-xs w-12 text-right shrink-0 font-mono">{pct}</span>
                  <MomentumArrow momentum={team.momentum} />
                  <span
                    className={`text-xs w-12 text-right shrink-0 font-mono ${
                      (team.compound || 0) >= 0.1 ? "text-emerald-400" : (team.compound || 0) <= -0.1 ? "text-red-400" : "text-white/40"
                    }`}
                  >
                    {(team.compound || 0) >= 0 ? "+" : ""}{(team.compound || 0).toFixed(2)}
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
