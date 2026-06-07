import type { ReactNode } from "react"

interface Props {
  label: string
  value: string | number | ReactNode
  sub?: string
  accent?: "green" | "red" | "amber" | "blue"
  loading?: boolean
  /** Shown on hover of a * next to the label */
  labelNote?: string
}

const accents = {
  green: "text-emerald-400",
  red:   "text-red-400",
  amber: "text-amber-400",
  blue:  "text-blue-400",
}

export default function StatCard({ label, value, sub, accent = "green", loading, labelNote }: Props) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col gap-1">
      {labelNote ? (
        <span className="relative group inline-flex items-start gap-0.5 w-fit">
          <span className="text-white/40 text-xs uppercase tracking-widest leading-snug">{label}</span>
          <span className="text-white/35 text-xs cursor-help leading-snug">*</span>
          <div
            role="tooltip"
            className="pointer-events-none absolute left-0 top-full z-20 mt-1.5 w-52 rounded-lg border border-white/15 bg-[#0a0a0e] px-2.5 py-2 text-[11px] text-white/75 normal-case tracking-normal opacity-0 shadow-xl transition-opacity group-hover:opacity-100"
          >
            {labelNote}
          </div>
        </span>
      ) : (
        <span className="text-white/40 text-xs uppercase tracking-widest">{label}</span>
      )}
      {loading ? (
        <div className="h-8 w-24 bg-white/10 rounded animate-pulse" />
      ) : (
        <div className={`text-2xl font-bold ${accents[accent]} flex items-center gap-2`}>{value}</div>
      )}
      {sub && <span className="text-white/40 text-xs">{sub}</span>}
    </div>
  )
}
