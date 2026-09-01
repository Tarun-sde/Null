import React from "react";
import { MapPin, Navigation } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { Site } from "@/types";

interface MiniMapProps {
  site?: Site | null;
  latitude?: number;
  longitude?: number;
}

export function MiniMap({ site, latitude = 37.7749, longitude = -122.4194 }: MiniMapProps) {
  return (
    <GlassCard variant="light" className="p-5 overflow-hidden flex flex-col justify-between h-full">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <MapPin className="size-3.5 text-[#ff5a24]" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-black">
            Geospatial Telemetry
          </h4>
        </div>
        <span className="text-[10px] font-mono text-[#7a7a7a]">
          {latitude.toFixed(4)}, {longitude.toFixed(4)}
        </span>
      </div>

      {/* Mini Radar Map Surface */}
      <div className="relative h-44 w-full rounded-xl border border-black/15 bg-[#eae7df] overflow-hidden shadow-inner flex items-center justify-center">
        {/* Grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.06)_1px,transparent_1px),linear-gradient(to_bottom,rgba(0,0,0,0.06)_1px,transparent_1px)] bg-[size:1.25rem_1.25rem] opacity-60" />

        {/* Concentric rings */}
        <div className="absolute size-32 rounded-full border border-black/10" />
        <div className="absolute size-20 rounded-full border border-dashed border-black/15" />
        <div className="absolute size-10 rounded-full border border-black/20 bg-black/5" />

        {/* Spinning scanner */}
        <div className="absolute size-32 rounded-full bg-[conic-gradient(from_0deg,transparent_0deg,transparent_270deg,rgba(255,90,36,0.15)_360deg)] animate-radar pointer-events-none" />

        {/* Center Target Pin */}
        <div className="relative z-10 flex flex-col items-center">
          <span className="size-4 rounded-full bg-[#ff5a24] border-2 border-white shadow-md flex items-center justify-center">
            <span className="size-1 rounded-full bg-white animate-pulse" />
          </span>
          {site && (
            <span className="text-[10px] font-bold text-black bg-white/90 px-2 py-0.5 rounded shadow-sm border border-black/10 mt-1 whitespace-nowrap">
              {site.name}
            </span>
          )}
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-[#6a6a6a]">
        <span>Current Site: <strong className="text-black">{site?.name || "Yard Staging"}</strong></span>
        <span className="text-[10px] text-emerald-600 font-medium">GPS Signal Locked</span>
      </div>
    </GlassCard>
  );
}
