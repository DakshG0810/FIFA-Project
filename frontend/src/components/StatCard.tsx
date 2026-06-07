import type { ReactNode } from "react"

interface Props {
  label: string
  value: string | number | ReactNode
  sub?: string
  accent?: "green" | "red" | "amber" | "blue"
  loading?: boolean
}

const accents = {
  green: "text-emerald-400",
  red:   "text-red-400",
  amber: "text-amber-400",
  blue:  "text-blue-400",
}

export default function StatCard({ label, value, sub, accent = "green", loading }: Props) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col gap-1">
      <span className="text-white/40 text-xs uppercase tracking-widest">{label}</span>
      {loading ? (
        <div className="h-8 w-24 bg-white/10 rounded animate-pulse" />
      ) : (
        <div className={`text-2xl font-bold ${accents[accent]} flex items-center gap-2`}>{value}</div>
      )}
      {sub && <span className="text-white/40 text-xs">{sub}</span>}
    </div>
  )
}
