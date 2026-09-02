"use client";

import React, { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import { MapPin } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { Site } from "@/types";

interface MiniMapProps {
  site?: Site | null;
  latitude?: number;
  longitude?: number;
}

export function MiniMap({ site, latitude = 18.7180, longitude = 81.2580 }: MiniMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markerRef = useRef<mapboxgl.Marker | null>(null);

  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
  const hasMapboxToken = Boolean(mapboxToken?.trim());
  const [mapboxError, setMapboxError] = useState<boolean>(false);
  const [isMapReady, setIsMapReady] = useState<boolean>(false);
  const initialCoordRef = useRef<[number, number]>([longitude, latitude]);

  // 1. Initialize MiniMap Mapbox Instance
  useEffect(() => {
    if (!mapboxToken || mapboxToken.trim() === "") {
      return;
    }

    if (!mapContainerRef.current) return;

    try {
      mapboxgl.accessToken = mapboxToken;

      const map = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: "mapbox://styles/mapbox/dark-v11",
        center: initialCoordRef.current,
        zoom: 14.2,
        attributionControl: false,
        interactive: false, // Read-only tactical minimap
      });

      map.on("load", () => {
        mapRef.current = map;
        setIsMapReady(true);
        setMapboxError(false);

        // Create Custom Asset Marker
        const el = document.createElement("div");
        el.className = "flex flex-col items-center select-none";
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            <span class="size-4 rounded-full bg-[#ff5a24] border-2 border-white shadow-md flex items-center justify-center">
              <span class="size-1 rounded-full bg-white animate-pulse"></span>
            </span>
          </div>
        `;

        const marker = new mapboxgl.Marker({ element: el, anchor: "center" })
          .setLngLat(initialCoordRef.current)
          .addTo(map);

        markerRef.current = marker;
      });

      map.on("error", (e) => {
        console.warn("MiniMap Mapbox error:", e);
        if (e.error && (e.error.message?.includes("forbidden") || e.error.message?.includes("unauthorized") || e.error.message?.includes("Invalid Token"))) {
          setMapboxError(true);
        }
      });

      return () => {
        if (markerRef.current) markerRef.current.remove();
        map.remove();
        mapRef.current = null;
        setIsMapReady(false);
      };
    } catch (err) {
      console.warn("Failed to initialize MiniMap Mapbox:", err);
      queueMicrotask(() => setMapboxError(true));
    }
  }, [mapboxToken]);

  // 2. Update Marker Position & Pan Map on Live Telemetry
  useEffect(() => {
    if (!isMapReady || !mapRef.current) return;

    if (markerRef.current) {
      markerRef.current.setLngLat([longitude, latitude]);
    }

    mapRef.current.easeTo({
      center: [longitude, latitude],
      duration: 1000,
    });
  }, [latitude, longitude, isMapReady]);

  const useFallback = !hasMapboxToken || mapboxError;

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
      <div className="relative h-44 w-full rounded-xl border border-black/15 bg-[#111111] overflow-hidden shadow-inner flex items-center justify-center">
        {/* 1. Real Geographic Base Layer */}
        {!useFallback ? (
          <div ref={mapContainerRef} className="absolute inset-0 size-full z-0" />
        ) : (
          /* Fallback Tactical Canvas */
          <div className="absolute inset-0 size-full bg-[#eae7df] z-0">
            <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.06)_1px,transparent_1px),linear-gradient(to_bottom,rgba(0,0,0,0.06)_1px,transparent_1px)] bg-[size:1.25rem_1.25rem] opacity-60" />
            <div className="absolute inset-0 flex items-center justify-center">
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
          </div>
        )}

        {/* 2. Tactical Concentric Rings & Radar Scanner Overlay */}
        <div className="absolute inset-0 pointer-events-none z-10 flex items-center justify-center">
          <div className="absolute size-32 rounded-full border border-white/10" />
          <div className="absolute size-20 rounded-full border border-dashed border-white/15" />
          <div className="absolute size-10 rounded-full border border-white/20 bg-white/5" />
          <div className="absolute size-32 rounded-full bg-[conic-gradient(from_0deg,transparent_0deg,transparent_270deg,rgba(255,90,36,0.15)_360deg)] animate-radar" />
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-[#6a6a6a]">
        <span>Current Site: <strong className="text-black">{site?.name || "Yard Staging"}</strong></span>
        <span className="text-[10px] text-emerald-600 font-medium flex items-center gap-1">
          <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
          GPS Signal Locked
        </span>
      </div>
    </GlassCard>
  );
}
