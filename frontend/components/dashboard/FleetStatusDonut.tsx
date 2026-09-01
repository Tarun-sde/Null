"use client";

import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { GlassCard } from "../ui/GlassCard";
import { STATUS_CONFIG } from "@/lib/constants";
import { EquipmentStatus } from "@/types";

interface FleetStatusDonutProps {
  statusCounts: Record<string, number>;
  totalEquipment: number;
}

export function FleetStatusDonut({
  statusCounts,
  totalEquipment,
}: FleetStatusDonutProps) {
  const data = Object.entries(statusCounts).map(([statusKey, count]) => {
    const norm = (statusKey.toUpperCase() as EquipmentStatus) in STATUS_CONFIG
      ? (statusKey.toUpperCase() as EquipmentStatus)
      : "UNASSIGNED";
    return {
      name: STATUS_CONFIG[norm]?.label || statusKey,
      rawStatus: norm,
      value: count,
      color: STATUS_CONFIG[norm]?.color || "#64748b",
    };
  });

  const activeCount = statusCounts["ACTIVE"] || 0;
  const activePercent = totalEquipment > 0 ? Math.round((activeCount / totalEquipment) * 100) : 0;

  return (
    <GlassCard variant="dark" className="p-7 flex flex-col justify-between h-full">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-[#ff5a24] animate-pulse" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-white/80">
              Fleet Status Breakdown
            </h3>
          </div>
          <span className="text-xs font-mono text-white/60">{totalEquipment} Total Units</span>
        </div>
        <p className="text-xs text-white/50 mt-1">Real-time derived state distribution</p>
      </div>

      {/* Donut Chart with Center Label */}
      <div className="relative my-4 h-52 w-full flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const p = payload[0];
                  return (
                    <div className="rounded-lg bg-black/90 border border-white/20 p-2.5 shadow-xl text-xs text-white">
                      <p className="font-semibold">{p.name}</p>
                      <p className="text-[#ff5a24] font-mono mt-0.5">{p.value} Assets</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={4}
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center Readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <p
            className="text-3xl font-medium tracking-tight text-white leading-none"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            {activePercent}%
          </p>
          <p className="text-[10px] text-white/60 uppercase tracking-widest mt-1">Active</p>
        </div>
      </div>

      {/* Legend Grid */}
      <div className="grid grid-cols-2 gap-2.5 pt-4 border-t border-white/10 text-xs">
        {data.map((item) => (
          <div key={item.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
              <span className="text-white/80 truncate text-[11px]">{item.name}</span>
            </div>
            <span className="font-mono text-white/90 text-[11px] font-semibold">{item.value}</span>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
