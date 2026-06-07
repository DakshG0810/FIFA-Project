import { useCallback } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import StatCard from "../components/StatCard"
import SentimentBar from "../components/SentimentBar"
import TeamFlag from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import BuzzVolume from "../components/BuzzVolume"
import SpikeHeatmap from "../components/SpikeHeatmap"
import MomentumArrow from "../components/MomentumArrow"
import type { SpikeAlert, TeamSentiment } from "../types"
import { TEAM_CONFEDERATION } from "../data/teams"
import { pickFanFavourite, fanFavouriteSub } from "../utils/fanFavourite"
import { pickBookmakerFavourite } from "../utils/bookmakerFavourite"

const CONF_COLORS: Record<string, string> = {
  UEFA: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  CONMEBOL: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  CONCACAF: "bg-red-500/20 text-red-300 border-red-500/30",
  AFC: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  CAF: "bg-pink-500/20 text-pink-300 border-pink-500/30",
  OFC: "bg-white/10 text-white/50 border-white/20",
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
  const topByOdds = pickBookmakerFavourite(leaderboard)
  const fanFavourite = pickFanFavourite(leaderboard)

  return (
    <div className="space-y-6 sm:space-y-8 w-full max-w-full">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-950 via-black to-black border border-emerald-500/20 p-5 sm:p-8">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_rgba(16,185,129,0.15),transparent_60%)]" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-xs font-medium tracking-widest uppercase">Live analytics</span>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-2 leading-none">
            The pulse of <span className="text-emerald-400">WC 2026</span>
          </h1>
          <p className="text-white/40 text-sm max-w-xl">
            Real-time fan sentiment from Bluesky · Search buzz from Google Trends · Win probabilities from bookmakers
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total mentions" value={totalMentions.toLocaleString()} sub="Bluesky posts" loading={loading} />
        <StatCard label="Avg positivity" value={`${avgPositivity}%`} sub="of all posts" accent="green" loading={loading} />
        <StatCard
          label="Bookmaker favourite"
          value={
            topByOdds ? (
              <>
                <TeamFlag team={topByOdds.team} size="sm" />
                {topByOdds.team}
              </>
            ) : (
              "—"
            )
          }
          sub={topByOdds ? `${((topByOdds.win_probability || 0) * 100).toFixed(1)}% chance` : "odds loading"}
          accent="amber"
          loading={loading}
        />
        <StatCard
          label="Most positively talked about"
          value={
            fanFavourite ? (
              <>
                <TeamFlag team={fanFavourite.team} size="sm" />
                {fanFavourite.team}
              </>
            ) : (
              "—"
            )
          }
          sub={fanFavourite ? fanFavouriteSub(fanFavourite) : "needs enough Bluesky posts"}
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
        <h2 className="text-white/50 text-xs uppercase tracking-widest mb-1">Team leaderboard</h2>
        <p className="text-white/30 text-[11px] mb-3">
          Posts total · Win % from bookmakers
        </p>
        {loading ? (
          <LoadingSkeleton rows={8} />
        ) : (
          <div className="space-y-1.5">
            <div className="hidden md:flex items-center gap-3 px-4 py-2 text-[10px] uppercase tracking-wider text-white/35 border-b border-white/10">
              <span className="w-5 shrink-0 text-right">#</span>
              <span className="w-6 shrink-0" aria-hidden />
              <span className="w-28 shrink-0">Team</span>
              <span className="w-24 shrink-0">Confed.</span>
              <span className="flex-1 min-w-0">Tone (+/−)</span>
              <span className="w-20 text-right shrink-0" title="Total Bluesky posts across all collection days">
                Posts
              </span>
              <span className="w-12 text-right shrink-0" title="Implied win probability from Odds API">
                Win %
              </span>
              <span className="w-4 shrink-0 text-center" title="Sentiment trend: first vs latest collection">
                Δ
              </span>
              <span className="relative group w-12 text-right shrink-0">
                <span className="cursor-help border-b border-dotted border-white/25">Sentiment</span>
                <div
                  role="tooltip"
                  className="pointer-events-none absolute right-0 top-full z-20 mt-2 w-56 rounded-lg border border-white/15 bg-[#0a0a0e] px-3 py-2 text-[11px] text-white/80 opacity-0 shadow-xl transition-opacity group-hover:opacity-100 normal-case tracking-normal text-left"
                >
                  <p className="font-medium text-white mb-1">Fan sentiment score</p>
                  <p>How positive or negative Bluesky posts sound about each team, averaged across collection days.</p>
                  <p className="text-white/50 mt-1">+1 = very positive · 0 = neutral · −1 = very negative</p>
                </div>
              </span>
            </div>
            {leaderboard.map((team, i) => {
              const conf = TEAM_CONFEDERATION[team.team] || "UEFA"
              const pct = team.win_probability ? `${(team.win_probability * 100).toFixed(1)}%` : "—"
              return (
                <div
                  key={team.team}
                  className="flex items-center gap-3 bg-white/5 hover:bg-white/8 border border-white/5 hover:border-white/10 rounded-xl px-4 py-3 transition-all"
                >
                  <span className="text-white/20 text-xs w-5 text-right shrink-0">{i + 1}</span>
                  <TeamFlag team={team.team} size="sm" />
                  <span className="text-white text-sm font-medium w-28 shrink-0">{team.team}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border hidden md:inline w-24 text-center shrink-0 ${CONF_COLORS[conf]}`}>
                    {conf}
                  </span>
                  <div className="flex-1 min-w-0 hidden md:block">
                    <SentimentBar positive={team.positive} negative={team.negative} size="sm" />
                  </div>
                  <span className="text-white text-xs w-20 text-right shrink-0 font-mono">
                    {(team.mentions || 0).toLocaleString()}
                  </span>
                  <span className="text-amber-400 text-xs w-12 text-right shrink-0 font-mono">{pct}</span>
                  <span className="w-4 flex justify-center shrink-0">
                    <MomentumArrow momentum={team.momentum} />
                  </span>
                  <span
                    className={`text-xs w-12 text-right shrink-0 font-mono ${
                      (team.compound || 0) >= 0.1 ? "text-emerald-400" : (team.compound || 0) <= -0.1 ? "text-red-400" : "text-white/70"
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
