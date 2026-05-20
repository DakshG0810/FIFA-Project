import { useApi } from "../hooks/useApi"
import { api } from "../api"
import TeamFlag from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"

const CONF_MAP: Record<string, string> = {
  Argentina:"CONMEBOL", France:"UEFA", England:"UEFA", Brazil:"CONMEBOL",
  Spain:"UEFA", Germany:"UEFA", Portugal:"UEFA", Netherlands:"UEFA",
  USA:"CONCACAF", Mexico:"CONCACAF", Canada:"CONCACAF", Morocco:"CAF",
  Senegal:"CAF", Japan:"AFC", "South Korea":"AFC", Australia:"AFC",
  Iran:"AFC", "Saudi Arabia":"AFC", Ecuador:"CONMEBOL", Uruguay:"CONMEBOL",
  Colombia:"CONMEBOL", Switzerland:"UEFA", Croatia:"UEFA", Serbia:"UEFA",
  Poland:"UEFA", Turkey:"UEFA", Nigeria:"CAF", Cameroon:"CAF",
  Venezuela:"CONMEBOL", Chile:"CONMEBOL", Peru:"CONMEBOL", "New Zealand":"OFC",
}

const CONF_HEX: Record<string, string> = {
  UEFA:"#378ADD", CONMEBOL:"#10b981", CONCACAF:"#ef4444",
  AFC:"#f59e0b", CAF:"#d4537e", OFC:"#888780",
}

export default function Trends() {
  const { data: trends, loading }   = useApi(() => api.trends(), [], 21_600_000)
  const { data: keywords, loading: kwLoading } = useApi(() => api.keywords(40), [], 60_000)

  const sorted = [...trends].sort((a: any, b: any) => (b.interest_score || 0) - (a.interest_score || 0))
  const chartData = sorted.slice(0, 20).map((t: any) => ({
    team:  t.team,
    score: t.interest_score || 0,
    color: CONF_HEX[CONF_MAP[t.team] || "UEFA"],
  }))

  const maxScore = Math.max(...sorted.map((t: any) => t.interest_score || 0), 1)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Search buzz</h1>
        <p className="text-white/40 text-sm">
          Google Trends search interest · 0–100 relative index · Updated every 6 hours
        </p>
      </div>

      {/* Bar chart — top 20 */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
        <h2 className="text-white/50 text-xs uppercase tracking-widest mb-4">Top 20 teams by search interest</h2>
        {loading ? (
          <div className="h-64 bg-white/5 rounded-lg animate-pulse" />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 20 }}>
              <XAxis type="number" domain={[0, 100]} tick={{ fill: "#ffffff30", fontSize: 10 }} />
              <YAxis
                type="category" dataKey="team"
                tick={{ fill: "#ffffff60", fontSize: 11 }}
                width={80}
              />
              <Tooltip
                contentStyle={{ background: "#0a0a0a", border: "1px solid #ffffff20", borderRadius: 8 }}
                formatter={(v: any) => [`${v}/100`, "Interest"]}
              />
              <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} fillOpacity={0.8} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
        <div className="flex flex-wrap gap-3 mt-3">
          {Object.entries(CONF_HEX).map(([conf, color]) => (
            <div key={conf} className="flex items-center gap-1.5 text-xs text-white/40">
              <span className="w-2 h-2 rounded-sm" style={{ background: color }} />
              {conf}
            </div>
          ))}
        </div>
      </div>

      {/* Full ranked list */}
      <div>
        <h2 className="text-white/50 text-xs uppercase tracking-widest mb-3">All 32 teams ranked</h2>
        {loading ? (
          <LoadingSkeleton rows={10} />
        ) : (
          <div className="space-y-1.5">
            {sorted.map((team: any, i: number) => {
              const score = team.interest_score || 0
              const conf  = CONF_MAP[team.team] || "UEFA"
              const pct   = (score / maxScore) * 100
              return (
                <div
                  key={team.team}
                  className="flex items-center gap-3 bg-white/5 border border-white/5 rounded-xl px-4 py-3"
                >
                  <span className="text-white/20 text-xs w-5 text-right">{i + 1}</span>
                  <TeamFlag team={team.team} size="sm" />
                  <span className="text-white text-sm font-medium w-28 shrink-0">{team.team}</span>
                  <div className="flex-1 bg-white/10 rounded-full h-1.5 hidden md:block">
                    <div
                      className="h-1.5 rounded-full transition-all"
                      style={{ width: `${pct}%`, background: CONF_HEX[conf] }}
                    />
                  </div>
                  <span className="font-mono text-sm text-white/60 w-16 text-right">{score}<span className="text-white/20">/100</span></span>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Buzzword section */}
      <div>
        <h2 className="text-white/50 text-xs uppercase tracking-widest mb-3">Top buzzwords right now</h2>
        <p className="text-white/20 text-xs mb-4">From Bluesky posts · Updated every 30 minutes</p>
        {kwLoading ? (
          <LoadingSkeleton rows={3} />
        ) : keywords.length === 0 ? (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-8 text-center text-white/30 text-sm">
            Keywords will appear once Bluesky data starts collecting
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw: any) => {
              const size = Math.max(12, Math.min(22, 12 + (kw.total_freq / keywords[0].total_freq) * 10))
              return (
                <span
                  key={kw.keyword}
                  className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-white/70 hover:text-white hover:bg-white/10 transition-all cursor-default"
                  style={{ fontSize: size }}
                  title={kw.team_association ? `Most associated: ${kw.team_association}` : undefined}
                >
                  {kw.keyword}
                  <span className="text-white/20 text-xs ml-1">{kw.total_freq}</span>
                </span>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
