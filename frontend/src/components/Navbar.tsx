import { useState } from "react"
import { Link, useLocation } from "react-router-dom"

const links = [
  { to: "/",          label: "Overview"   },
  { to: "/sentiment", label: "Sentiment"  },
  { to: "/odds",      label: "Odds"       },
  { to: "/trends",    label: "Buzz"       },
  { to: "/analytics", label: "Analytics"  },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const [open, setOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/60 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-black font-black text-sm">
            W
          </div>
          <span className="font-bold text-white tracking-tight">
            PulseCup
            <span className="text-emerald-400 ml-1 text-xs font-normal">WC26</span>
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {links.map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={`px-3 py-1.5 rounded-md text-sm transition-all ${
                pathname === l.to
                  ? "bg-emerald-500/20 text-emerald-400 font-medium"
                  : "text-white/50 hover:text-white hover:bg-white/5"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>

        {/* Live badge */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          LIVE
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden text-white/70 hover:text-white p-1"
          onClick={() => setOpen(!open)}
        >
          <div className="w-5 h-px bg-current mb-1" />
          <div className="w-5 h-px bg-current mb-1" />
          <div className="w-5 h-px bg-current" />
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden border-t border-white/10 bg-black/90 px-4 py-3 flex flex-col gap-1">
          {links.map(l => (
            <Link
              key={l.to}
              to={l.to}
              onClick={() => setOpen(false)}
              className={`px-3 py-2 rounded-md text-sm ${
                pathname === l.to
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "text-white/60 hover:text-white"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}
