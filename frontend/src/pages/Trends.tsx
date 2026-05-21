import { useCallback } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"

type TrendItem = {
  team: string
  interest_score: number
  region: string
  captured_at: string
}

export default function Trends() {

  const fetchTrends = useCallback(async () => {
    const data = await api.trends()

    if (!Array.isArray(data)) {
      return []
    }

    return data
  }, [])

  const {
    data: trends,
    loading
  } = useApi<TrendItem[]>(
    fetchTrends,
    [],
    30000
  )

  if (loading) {
    return (
      <div className="text-white p-10">
        Loading trends...
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">

      <div>
        <h1 className="text-4xl font-bold text-white">
          Google Trends
        </h1>

        <p className="text-white/50">
          Live FIFA World Cup search interest
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">

        {trends.map((team, index) => (

          <div
            key={`${team.team}-${index}`}
            className="bg-white/5 border border-white/10 rounded-2xl p-5"
          >

            <div className="flex items-center justify-between">

              <div>
                <h2 className="text-2xl font-semibold text-white">
                  {team.team}
                </h2>

                <p className="text-white/40 text-sm">
                  {team.region}
                </p>
              </div>

              <div className="text-right">

                <div className="text-4xl font-bold text-emerald-400">
                  {team.interest_score}
                </div>

                <div className="text-white/40 text-sm">
                  trend score
                </div>

              </div>

            </div>

          </div>

        ))}

      </div>

    </div>
  )
}