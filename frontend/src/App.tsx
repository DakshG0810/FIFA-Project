import { BrowserRouter, Routes, Route } from "react-router-dom"
import Navbar from "./components/Navbar"
import DataFreshnessBar from "./components/DataFreshnessBar"
import Overview  from "./pages/Overview"
import Sentiment from "./pages/Sentiment"
import Odds      from "./pages/Odds"
import Trends    from "./pages/Trends"
import Analytics from "./pages/Analytics"

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#060608] text-white">

        {/* Subtle background texture */}
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(16,185,129,0.06),transparent_50%)]" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_rgba(59,130,246,0.04),transparent_50%)]" />
        </div>

        <Navbar />

        <main className="relative max-w-7xl mx-auto px-4 pt-20 pb-16">
          <Routes>
            <Route path="/"          element={<Overview  />} />
            <Route path="/sentiment" element={<Sentiment />} />
            <Route path="/odds"      element={<Odds      />} />
            <Route path="/trends"    element={<Trends    />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>

        <DataFreshnessBar />
      </div>
    </BrowserRouter>
  )
}
