import { useEffect, useState } from "react"

/** Matches Tailwind `md` breakpoint (< 768px). */
export function useIsMobile(breakpointPx = 768) {
  const [isMobile, setIsMobile] = useState(
    () => typeof window !== "undefined" && window.innerWidth < breakpointPx
  )

  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${breakpointPx - 1}px)`)
    const update = () => setIsMobile(mq.matches)
    update()
    mq.addEventListener("change", update)
    return () => mq.removeEventListener("change", update)
  }, [breakpointPx])

  return isMobile
}
