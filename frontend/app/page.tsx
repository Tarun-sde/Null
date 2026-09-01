import { Radio, Activity, CheckCircle2, Terminal } from "lucide-react";

export default function Home() {
  return (
    <main className="relative min-h-screen w-full overflow-hidden flex flex-col justify-between p-6 sm:p-10 lg:p-16">
      {/* Header */}
      <header className="flex w-full items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <span className="size-3 bg-[#ff5a24] shadow-[0_0_0_1px_rgba(255,90,36,0.18)]" />
          <span className="text-2xl font-medium tracking-[0.22em] text-black">
            RENTSENSE
          </span>
        </div>
        <div className="flex items-center gap-3 rounded-full border border-black/10 bg-white/60 px-4 py-1.5 backdrop-blur shadow-sm">
          <span className="size-2 rounded-full bg-[#ff5a24] animate-pulse" />
          <span className="text-xs font-medium tracking-wide uppercase text-[#222222]">
            Control Tower — Phase 0 Ready
          </span>
        </div>
      </header>

      {/* Center Hero Card */}
      <section className="my-auto mx-auto w-full max-w-4xl z-10 py-12">
        <div className="relative overflow-hidden rounded-[2rem] border border-black/15 bg-white/40 p-8 sm:p-12 shadow-[0_32px_80px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.72)] backdrop-blur-sm">
          {/* Subtle Accent Corner */}
          <div className="absolute right-6 top-6 h-12 w-12 border-r border-t border-black/15" />
          <div className="absolute bottom-6 left-6 h-12 w-12 border-b border-l border-black/15" />

          <div className="flex items-center gap-3 text-xs font-medium uppercase tracking-wide text-[#222222] mb-6">
            <span className="size-2.5 bg-[#ff5a24]" />
            <span>FLEET INTELLIGENCE &amp; RENTAL TRACKING</span>
          </div>

          <h1
            className="text-4xl sm:text-5xl lg:text-6xl font-medium leading-[1.05] tracking-tight text-black"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            RentSense{" "}
            <span className="italic text-[#ff5a24]">Control Tower</span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg sm:text-xl font-normal leading-snug text-[#252525]">
            Autonomous rental tracking and fleet intelligence system for construction and heavy equipment operations.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-black/10 bg-white/80 p-5 shadow-sm">
              <div className="flex items-center justify-between text-xs text-[#6a6a6a] uppercase font-medium">
                <span>Frontend Status</span>
                <CheckCircle2 className="size-4 text-[#ff5a24]" />
              </div>
              <p className="mt-3 text-2xl font-semibold text-black">Next.js App</p>
              <p className="mt-1 text-xs text-[#7a7a7a]">TypeScript &amp; Tailwind</p>
            </div>

            <div className="rounded-xl border border-black/10 bg-white/80 p-5 shadow-sm">
              <div className="flex items-center justify-between text-xs text-[#6a6a6a] uppercase font-medium">
                <span>Backend Status</span>
                <Radio className="size-4 text-[#ff5a24] animate-pulse" />
              </div>
              <p className="mt-3 text-2xl font-semibold text-black">FastAPI</p>
              <p className="mt-1 text-xs text-[#7a7a7a]">Python &amp; Uvicorn</p>
            </div>

            <div className="rounded-xl border border-black/10 bg-white/80 p-5 shadow-sm">
              <div className="flex items-center justify-between text-xs text-[#6a6a6a] uppercase font-medium">
                <span>Phase Status</span>
                <Activity className="size-4 text-[#ff5a24]" />
              </div>
              <p className="mt-3 text-2xl font-semibold text-black">Phase 0</p>
              <p className="mt-1 text-xs text-[#7a7a7a]">Foundation Established</p>
            </div>
          </div>

          <div className="mt-8 flex flex-col sm:flex-row items-center gap-4">
            <div className="flex items-center gap-3 rounded-lg border border-black/15 bg-[#111111] px-6 py-3.5 text-sm font-medium text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.14)]">
              <Terminal className="size-4 text-[#ff5a24]" />
              <span>Ready for Phase 1 Data Models &amp; Core APIs</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="flex flex-col sm:flex-row items-center justify-between text-xs text-[#6a6a6a] z-10 pt-6 border-t border-black/10">
        <p>&copy; {new Date().getFullYear()} RentSense Control Tower. Operational Elegance Architecture.</p>
        <div className="flex items-center gap-6 mt-4 sm:mt-0">
          <span>Target Stack: Next.js + FastAPI + PostgreSQL</span>
        </div>
      </footer>
    </main>
  );
}
