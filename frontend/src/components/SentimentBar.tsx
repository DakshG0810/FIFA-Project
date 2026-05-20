interface Props {
  positive: number
  negative: number
  neutral?: number
  size?: "sm" | "md"
}

export default function SentimentBar({ positive, negative, neutral, size = "md" }: Props) {
  const h = size === "sm" ? "h-1.5" : "h-2.5"
  const pos = Math.round((positive || 0) * 100)
  const neg = Math.round((negative || 0) * 100)
  const neu = Math.max(0, 100 - pos - neg)

  return (
    <div className={`w-full ${h} rounded-full overflow-hidden flex bg-white/10`}>
      <div
        className="bg-emerald-500 transition-all duration-700"
        style={{ width: `${pos}%` }}
        title={`Positive: ${pos}%`}
      />
      <div
        className="bg-white/20 transition-all duration-700"
        style={{ width: `${neu}%` }}
        title={`Neutral: ${neu}%`}
      />
      <div
        className="bg-red-500 transition-all duration-700"
        style={{ width: `${neg}%` }}
        title={`Negative: ${neg}%`}
      />
    </div>
  )
}
