"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MapPin, Navigation, RefreshCw, Maximize2, Layers } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { StatusBadge } from "../ui/StatusBadge";
import { SITE_COORDINATES, STATUS_CONFIG } from "@/lib/constants";
import { EquipmentListItem, EquipmentStatus } from "@/types";
import { cn } from "@/lib/utils";

interface FleetMapCardProps {
  equipmentList: EquipmentListItem[];
}

export function FleetMapCard({ equipmentList }: FleetMapCardProps) {
  const [selectedSiteId, setSelectedSiteId] = useState<string>("ALL");
  const [activeAssetHover, setActiveAssetHover] = useState<EquipmentListItem | null>(null);

  const filteredAssets = selectedSiteId === "ALL"
    ? equipmentList
    : equipmentList.filter((eq) => eq.site?.id === selectedSiteId);

  // Normalization for SVG map canvas representation of the 3 SF Bay locations
  // Lat range ~ 37.75 to 37.82 -> Y (0 to 100%)
  // Lng range ~ -122.46 to -122.26 -> X (0 to 100%)
  const minLat = 37.74;
  const maxLat = 37.82;
  const minLng = -122.48;
  const maxLng = -122.25;

  const projectCoord = (lat: number, lng: number) => {
    const x = ((lng - minLng) / (maxLng - minLng)) * 100;
    const y = (1 - (lat - minLat) / (maxLat - minLat)) * 100;
    return {
      left: `${Math.min(92, Math.max(8, x))}%`,
      top: `${Math.min(88, Math.max(12, y))}%`,
    };
  };

  return (
    <GlassCard variant="light" className="p-7 overflow-hidden relative flex flex-col justify-between">
      {/* Card Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className="size-2 bg-[#ff5a24] shadow-[0_0_0_1px_rgba(255,90,36,0.2)]" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
              Tactical Fleet Map
            </h3>
          </div>
          <p className="text-xs text-[#6a6a6a] mt-0.5">
            Geospatial fleet coordinates &amp; site surveillance grid
          </p>
        </div>

        {/* Site Filter Tabs */}
        <div className="flex items-center gap-1.5 rounded-xl border border-black/10 bg-white/70 p-1 text-xs shadow-sm">
          <button
            onClick={() => setSelectedSiteId("ALL")}
            className={cn(
              "px-3 py-1 rounded-lg font-medium transition-all",
              selectedSiteId === "ALL"
                ? "bg-[#111111] text-white shadow-sm"
                : "text-[#555] hover:text-black"
            )}
          >
            All Sites ({equipmentList.length})
          </button>
          {SITE_COORDINATES.map((site) => (
            <button
              key={site.id}
              onClick={() => setSelectedSiteId(site.id)}
              className={cn(
                "px-3 py-1 rounded-lg font-medium transition-all hidden md:block",
                selectedSiteId === site.id
                  ? "bg-[#111111] text-white shadow-sm"
                  : "text-[#555] hover:text-black"
              )}
            >
              {site.name.split(" ")[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Centerpiece Map View Area */}
      <div className="relative my-6 h-80 sm:h-96 w-full rounded-2xl border border-black/15 bg-[#eae7df] overflow-hidden shadow-inner">
        {/* Vector Background Map Grid & Radial Scan Rings */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.7),transparent_70%)] pointer-events-none" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(0,0,0,0.05)_1px,transparent_1px)] bg-[size:2rem_2rem] opacity-70 pointer-events-none" />

        {/* Tactical Crosshairs & Radar Scanner */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-72 rounded-full border border-black/10 pointer-events-none" />
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-48 rounded-full border border-dashed border-black/15 pointer-events-none" />
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-24 rounded-full border border-black/10 pointer-events-none" />
        <div className="absolute left-1/2 top-0 bottom-0 w-px -translate-x-1/2 bg-black/10 pointer-events-none" />
        <div className="absolute top-1/2 left-0 right-0 h-px -translate-y-1/2 bg-black/10 pointer-events-none" />

        {/* Spinning Radar Beam */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-72 rounded-full bg-[conic-gradient(from_0deg,transparent_0deg,transparent_270deg,rgba(255,90,36,0.12)_360deg)] animate-radar pointer-events-none" />

        {/* Render Site Landmark Zones */}
        {SITE_COORDINATES.map((site) => {
          const coords = projectCoord(site.lat, site.lng);
          return (
            <div
              key={site.id}
              style={{ left: coords.left, top: coords.top }}
              className="absolute -translate-x-1/2 -translate-y-1/2 pointer-events-none flex flex-col items-center"
            >
              <div className="size-16 rounded-full border border-black/10 bg-white/30 backdrop-blur-[2px]" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-black/70 mt-1 bg-white/80 px-2 py-0.5 rounded shadow-sm border border-black/10">
                {site.name}
              </span>
            </div>
          );
        })}

        {/* Render Asset Pins */}
        {filteredAssets.map((asset) => {
          const lat = asset.latest_telemetry?.latitude || (asset.site ? 37.7749 : 37.7610);
          const lng = asset.latest_telemetry?.longitude || (asset.site ? -122.4194 : -122.4480);
          const pos = projectCoord(lat, lng);
          const normStatus = (asset.status.toUpperCase() as EquipmentStatus) in STATUS_CONFIG
            ? (asset.status.toUpperCase() as EquipmentStatus)
            : "UNASSIGNED";
          const color = STATUS_CONFIG[normStatus].color;

          return (
            <Link
              key={asset.id}
              href={`/assets/${asset.id}`}
              style={{ left: pos.left, top: pos.top }}
              onMouseEnter={() => setActiveAssetHover(asset)}
              onMouseLeave={() => setActiveAssetHover(null)}
              className="absolute -translate-x-1/2 -translate-y-1/2 group z-20 transition-transform hover:scale-125"
            >
              <div className="relative flex items-center justify-center">
                <span
                  className="size-5 rounded-full shadow-lg border-2 border-white flex items-center justify-center transition-all group-hover:ring-4 group-hover:ring-black/10"
                  style={{ backgroundColor: color }}
                >
                  <span className="size-1.5 rounded-full bg-white animate-pulse" />
                </span>

                {/* Tooltip Tag */}
                <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col items-center whitespace-nowrap rounded-xl bg-[#111111] px-3 py-2 text-xs text-white shadow-2xl border border-white/20 z-30">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[#ff5a24]">{asset.id}</span>
                    <span>•</span>
                    <span>{asset.type}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-white/70">
                    <span>{STATUS_CONFIG[normStatus].label}</span>
                    <span>|</span>
                    <span>{asset.site?.name || "Yard Staging"}</span>
                  </div>
                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[#111111]" />
                </div>
              </div>
            </Link>
          );
        })}

        {/* Map Overlay Controls */}
        <div className="absolute bottom-4 right-4 flex items-center gap-2 z-10">
          <button
            onClick={() => setSelectedSiteId("ALL")}
            className="flex items-center gap-1.5 rounded-lg border border-black/10 bg-white/90 px-3 py-1.5 text-xs font-medium text-black shadow-sm hover:bg-white transition-colors"
          >
            <Navigation className="size-3 text-[#ff5a24]" />
            <span>Center Fleet</span>
          </button>
        </div>

        {/* Live Legend Bar */}
        <div className="absolute bottom-4 left-4 hidden sm:flex items-center gap-3 rounded-lg border border-black/10 bg-white/80 px-3 py-1.5 text-[11px] backdrop-blur shadow-sm z-10">
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-emerald-500" />
            <span className="text-black font-medium">Active</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-amber-500" />
            <span className="text-black font-medium">Idle</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-[#ff5a24]" />
            <span className="text-black font-medium">Due Soon</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-red-600" />
            <span className="text-black font-medium">Overdue</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-slate-400" />
            <span className="text-black font-medium">Unassigned</span>
          </div>
        </div>
      </div>
    </GlassCard>
  );
}
