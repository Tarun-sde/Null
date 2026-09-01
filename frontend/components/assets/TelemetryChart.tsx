"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { GlassCard } from "../ui/GlassCard";
import { Telemetry } from "@/types";

interface TelemetryChartProps {
  telemetry: Telemetry[];
  title?: string;
}

export function TelemetryChart({
  telemetry,
  title = "Telemetry Runtime & Utilization History",
}: TelemetryChartProps) {
  // Sort chronological
  const sortedData = [...telemetry].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  const formattedData = sortedData.map((t, idx) => {
    const d = new Date(t.timestamp);
    const timeLabel = `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
    const activeHours = Math.max(0, t.engine_hours - t.idle_hours);

    return {
      time: timeLabel,
      engine_hours: t.engine_hours,
      active_hours: parseFloat(activeHours.toFixed(1)),
      idle_hours: t.idle_hours,
      fuel_pct: t.fuel_pct,
    };
  });

  return (
    <GlassCard variant="dark" className="p-7 overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-white/10">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-white">
            {title}
          </h3>
          <p className="text-xs text-white/50 mt-0.5">
            Engine runtime vs idle duration telemetry stream
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-[#ff5a24]" />
            <span className="text-white/80">Active Hours</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-amber-400" />
            <span className="text-white/80">Idle Hours</span>
          </div>
        </div>
      </div>

      {/* Chart Area */}
      <div className="mt-6 h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="activeGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff5a24" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#ff5a24" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="idleGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#fbbf24" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
            <XAxis
              dataKey="time"
              stroke="rgba(255,255,255,0.4)"
              fontSize={10}
              tickLine={false}
            />
            <YAxis
              stroke="rgba(255,255,255,0.4)"
              fontSize={10}
              tickLine={false}
              unit="h"
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="rounded-xl bg-black/95 border border-white/20 p-3 shadow-2xl text-xs text-white">
                      <p className="font-mono text-white/60 mb-1">Time: {label}</p>
                      {payload.map((entry, index) => (
                        <p key={`item-${index}`} className="font-semibold" style={{ color: entry.color }}>
                          {entry.name}: {entry.value}h
                        </p>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area
              type="monotone"
              dataKey="active_hours"
              name="Active Hours"
              stroke="#ff5a24"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#activeGrad)"
            />
            <Area
              type="monotone"
              dataKey="idle_hours"
              name="Idle Hours"
              stroke="#fbbf24"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#idleGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
