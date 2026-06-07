import { useState, useCallback, useMemo } from "react"

import { useApi } from "../hooks/useApi"

import { api } from "../api"

import TeamFlag from "../components/TeamFlag"

import { WC_TEAMS } from "../data/teams"

import DataBadge from "../components/DataBadge"

import { useDataMode } from "../hooks/useDataMode"

import type { InterestOddsData } from "../types"

import {

  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Legend,

} from "recharts"



const TEAM_COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]



const METHODOLOGY_INTEREST_ODDS =

  "Odds: tournament winner outrights averaged across bookmakers. Total interest: average rank of Google Trends search score and Bluesky post volume (1 = highest). Convergence: interest rank and odds rank within 4 places of each other. Divergence columns: gap ≥ 5 ranks, excluding convergence teams."



const METHODOLOGY_NARRATIVE =

  "Tracks how Bluesky fan tone shifts day by day for each team. Each point is one calendar day: we average post sentiment (VADER compound score from −1 negative to +1 positive) across posts collected that day. Select up to 4 teams to compare narrative momentum over time."



function InterestOddsCard({

  row,

  insight,

  bigGap,

}: {

  row: InterestOddsData["convergence"][0]

  insight: string

  bigGap?: boolean

}) {

  return (

    <div className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 space-y-1">

      <div className="flex items-center gap-3">

        <TeamFlag team={row.team} size="sm" />

        <div className="flex-1 min-w-0">

          <div className="text-white text-sm font-medium flex items-center gap-2">

            {row.team}

            {bigGap && <span className="text-amber-400" title="Large divergence">⚡</span>}

          </div>

          <div className="text-white/40 text-xs">

            Odds #{row.odds_rank} · Interest #{row.interest_rank} · {row.win_probability}% win

          </div>

        </div>

      </div>

      <p className="text-white/50 text-xs pl-9">{insight}</p>

    </div>

  )

}



export default function Analytics() {

  const badge = useDataMode("bluesky")

  const [selected, setSelected] = useState(["Argentina", "France", "England", "Brazil"])



  const fetchNarrative = useCallback(() => api.narrative(selected), [selected])

  const fetchInterestOdds = useCallback(() => api.interestOdds(), [])



  const { data: narrative, loading: narrativeLoading } = useApi(fetchNarrative, { teams: [], points: [] }, 120000)

  const { data: interestOdds, loading: interestLoading } = useApi<InterestOddsData>(

    fetchInterestOdds,

    { convergence: [], higher_odds_lower_interest: [], higher_interest_lower_odds: [] },

    120000

  )



  const chartData = useMemo(() => {

    return narrative.points.map((p) => {

      const row: Record<string, string | number> = {

        time: new Date(p.time + "T12:00:00").toLocaleString("en", { month: "short", day: "numeric" }),

      }

      for (const team of narrative.teams) {

        if (typeof p[team] === "number") row[team] = p[team] as number

      }

      return row

    })

  }, [narrative])



  const toggleTeam = (team: string) => {

    setSelected((prev) => {

      if (prev.includes(team)) return prev.filter((t) => t !== team)

      if (prev.length >= 4) return prev

      return [...prev, team]

    })

  }



  return (

    <div className="space-y-6 sm:space-y-8 w-full max-w-full">

      <div>

        <h1 className="text-3xl font-bold text-white mb-2">Analytics</h1>

        <p className="text-white/40 text-sm">Narrative shift · interest vs odds convergence & divergence</p>

      </div>



      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">

        <div className="flex items-center gap-2">

          <h2 className="text-white font-semibold">Narrative Shift</h2>

          <DataBadge mode={badge} />

        </div>

        <div className="relative group max-w-2xl">
          <p className="text-white/40 text-xs cursor-help underline decoration-dotted decoration-white/25 underline-offset-2">
            Compound sentiment · up to 4 teams · Please hover for methodology
          </p>
          <div
            role="tooltip"
            className="pointer-events-none absolute left-0 top-full z-20 mt-2 w-full max-w-md rounded-lg border border-white/15 bg-[#0a0a0e] px-3 py-2.5 text-[11px] text-white/75 opacity-0 shadow-xl transition-opacity group-hover:opacity-100"
          >
            <p>{METHODOLOGY_NARRATIVE}</p>
          </div>
        </div>



        <div className="flex flex-wrap gap-2">

          {WC_TEAMS.map((team) => {

            const isSelected = selected.includes(team)

            const colorIndex = selected.indexOf(team)

            return (

              <button

                key={team}

                onClick={() => toggleTeam(team)}

                className={`px-3 py-1.5 rounded-full text-xs border transition-all ${

                  isSelected ? "text-black border-transparent" : "bg-white/5 border-white/10 text-white/60"

                }`}

                style={isSelected ? { background: TEAM_COLORS[colorIndex] } : {}}

              >

                <span className="inline-flex items-center gap-1">

                  <TeamFlag team={team} size="sm" />

                  {team}

                </span>

              </button>

            )

          })}

        </div>



        {narrativeLoading ? (

          <div className="h-[300px] bg-white/5 rounded-lg animate-pulse" />

        ) : chartData.length === 0 ? (

          <p className="text-white/30 text-sm py-12 text-center">No narrative history yet</p>

        ) : (

          <ResponsiveContainer width="100%" height={300}>

            <LineChart data={chartData}>

              <XAxis dataKey="time" tick={{ fill: "#ffffff40", fontSize: 9 }} interval="preserveStartEnd" />

              <YAxis domain={[-1, 1]} tick={{ fill: "#ffffff40", fontSize: 10 }} />

              <Tooltip contentStyle={{ background: "#111", border: "1px solid #333" }} />

              <Legend />

              <ReferenceLine y={0} stroke="#ffffff20" strokeDasharray="3 3" />

              {selected.map((team, i) => (

                <Line key={team} type="monotone" dataKey={team} stroke={TEAM_COLORS[i]} strokeWidth={2} dot={{ r: 3 }} />

              ))}

            </LineChart>

          </ResponsiveContainer>

        )}

      </div>



      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">

        <div>

          <h2 className="text-white font-semibold">Convergence & Divergence</h2>

          <p

            className="text-white/40 text-xs mt-1 cursor-help"

            title={METHODOLOGY_INTEREST_ODDS}

          >

            Total interest (Google Trends + Bluesky) vs Bookmakers win probability

            <br />

            Please hover for methodology

          </p>

        </div>



        {interestLoading ? (

          <div className="h-40 bg-white/5 rounded-lg animate-pulse" />

        ) : (

          <>

            {interestOdds.convergence.length > 0 && (

              <div className="space-y-2">

                <p className="text-emerald-400/80 text-xs font-medium uppercase tracking-wide">

                  Convergence — aligned hype & expectations

                </p>

                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">

                  {interestOdds.convergence.map((row) => (

                    <InterestOddsCard

                      key={row.team}

                      row={row}

                      insight="Bookmakers and fans both tracking this team closely."

                    />

                  ))}

                </div>

              </div>

            )}



            <div className="grid md:grid-cols-2 gap-4 pt-2">

              <div className="space-y-2">

                <p className="text-white/60 text-xs font-medium">Divergence — higher odds, lower interest</p>

                <p className="text-white/30 text-[11px] mb-2">

                  Strong win probability but less search/buzz — may be flying under the radar.

                </p>

                {interestOdds.higher_odds_lower_interest.length === 0 ? (

                  <p className="text-white/20 text-sm py-4 text-center">No large gaps yet</p>

                ) : (

                  interestOdds.higher_odds_lower_interest.slice(0, 8).map((row) => (

                    <InterestOddsCard

                      key={row.team}

                      row={row}

                      bigGap={row.interest_rank - row.odds_rank > 5}

                      insight="Less fan/search appeal than bookmakers suggest."

                    />

                  ))

                )}

              </div>



              <div className="space-y-2">

                <p className="text-white/60 text-xs font-medium">Divergence — higher interest, lower odds</p>

                <p className="text-white/30 text-[11px] mb-2">

                  More buzz than betting markets price in — positive chatter / dark horse territory.

                </p>

                {interestOdds.higher_interest_lower_odds.length === 0 ? (

                  <p className="text-white/20 text-sm py-4 text-center">No large gaps yet</p>

                ) : (

                  interestOdds.higher_interest_lower_odds.slice(0, 8).map((row) => (

                    <InterestOddsCard

                      key={row.team}

                      row={row}

                      bigGap={row.odds_rank - row.interest_rank > 5}

                      insight="Public following exceeds betting expectations."

                    />

                  ))

                )}

              </div>

            </div>

          </>

        )}

      </div>

    </div>

  )

}


