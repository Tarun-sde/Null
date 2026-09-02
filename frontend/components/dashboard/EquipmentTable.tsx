"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, Truck, ChevronRight } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { StatusBadge } from "../ui/StatusBadge";
import { EquipmentListItem } from "@/types";
import { cn, formatDayRate } from "@/lib/utils";

interface EquipmentTableProps {
  equipmentList: EquipmentListItem[];
}

export function EquipmentTable({ equipmentList }: EquipmentTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const filteredList = equipmentList.filter((eq) => {
    const matchesSearch =
      eq.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eq.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eq.dealer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (eq.site?.name && eq.site.name.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus =
      statusFilter === "ALL" || eq.status.toUpperCase() === statusFilter.toUpperCase();

    return matchesSearch && matchesStatus;
  });

  return (
    <GlassCard variant="light" className="p-7 overflow-hidden">
      {/* Table Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-black/10">
        <div>
          <div className="flex items-center gap-2">
            <Truck className="size-4 text-[#ff5a24]" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-black">
              Equipment Fleet Ledger
            </h3>
          </div>
          <p className="text-xs text-[#6a6a6a] mt-0.5">
            Active rental contracts, telemetry diagnostics, and operational status
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-[#7a7a7a]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter ledger..."
              className="rounded-xl border border-black/10 bg-white/70 pl-8 pr-3 py-1.5 text-xs text-black placeholder:text-[#8a8a8a] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#ff5a24]"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-black/10 bg-white/70 px-3 py-1.5 text-xs text-black focus:outline-none focus:ring-1 focus:ring-[#ff5a24]"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="IDLE">Idle / Low Use</option>
            <option value="DUE_SOON">Due Soon</option>
            <option value="OVERDUE">Overdue</option>
            <option value="UNASSIGNED">Unassigned</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          {/* Table Header */}
          <thead>
            <tr className="border-b border-black/10 text-[11px] font-semibold text-[#6a6a6a] uppercase tracking-wider">
              <th className="py-3 px-3">Asset ID &amp; Model</th>
              <th className="py-3 px-3">Equipment Type</th>
              <th className="py-3 px-3">Assigned Site</th>
              <th className="py-3 px-3">Operator</th>
              <th className="py-3 px-3">Daily Rate</th>
              <th className="py-3 px-3">Utilization</th>
              <th className="py-3 px-3 text-center">Status</th>
              <th className="py-3 px-3 text-right">Detail</th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="divide-y divide-black/5">
            {filteredList.map((eq) => {
              const model = (eq.metadata_json as { model?: string } | null)?.model || "Standard Spec";
              const utilPct = Math.round(eq.utilization_rate * 100);
              const fuelPct = eq.latest_telemetry?.fuel_pct ?? 100;

              return (
                <tr
                  key={eq.id}
                  className="group hover:bg-black/[0.03] transition-colors rounded-xl cursor-pointer"
                >
                  {/* Asset ID & Model */}
                  <td className="py-3.5 px-3">
                    <Link href={`/assets/${eq.id}`} className="block">
                      <span className="font-bold text-black group-hover:text-[#ff5a24] transition-colors">
                        {eq.id}
                      </span>
                      <span className="text-[11px] text-[#7a7a7a] block mt-0.5">
                        {model}
                      </span>
                    </Link>
                  </td>

                  {/* Equipment Type */}
                  <td className="py-3.5 px-3 font-medium text-black">
                    {eq.type}
                    <span className="text-[10px] text-[#7a7a7a] block">{eq.dealer}</span>
                  </td>

                  {/* Assigned Site */}
                  <td className="py-3.5 px-3 text-[#333]">
                    {eq.site ? (
                      <div>
                        <span className="font-medium block">{eq.site.name}</span>
                        <span className="text-[10px] text-[#7a7a7a] block truncate max-w-40">
                          {eq.site.location}
                        </span>
                      </div>
                    ) : (
                      <span className="text-[#8a8a8a] italic font-mono">Yard Staging</span>
                    )}
                  </td>

                  {/* Operator */}
                  <td className="py-3.5 px-3">
                    {eq.operator ? (
                      <div className="flex items-center gap-2">
                        <div className="size-6 rounded-full bg-black/10 text-black text-[10px] font-bold grid place-items-center">
                          {eq.operator.name.charAt(0)}
                        </div>
                        <span className="font-medium text-black">{eq.operator.name}</span>
                      </div>
                    ) : (
                      <span className="text-[#ff5a24] font-medium text-[11px] bg-orange-50 px-2 py-0.5 rounded border border-[#ff5a24]/30">
                        Unassigned
                      </span>
                    )}
                  </td>

                  {/* Daily Rate */}
                  <td className="py-3.5 px-3 font-mono font-semibold text-black">
                    {formatDayRate(eq.daily_rate, "/d")}
                  </td>

                  {/* Utilization & Fuel */}
                  <td className="py-3.5 px-3">
                    <div className="w-28 space-y-1">
                      <div className="flex items-center justify-between text-[10px] text-[#666]">
                        <span>{utilPct}% Use</span>
                        <span>{fuelPct}% Fuel</span>
                      </div>
                      <div className="h-1.5 w-full bg-black/10 rounded-full overflow-hidden">
                        <div
                          className={cn(
                            "h-full rounded-full transition-all",
                            utilPct < 20 ? "bg-amber-500" : "bg-[#ff5a24]"
                          )}
                          style={{ width: `${Math.min(100, Math.max(8, utilPct))}%` }}
                        />
                      </div>
                    </div>
                  </td>

                  {/* Status Badge */}
                  <td className="py-3.5 px-3 text-center">
                    <StatusBadge status={eq.status} size="sm" />
                  </td>

                  {/* Detail Action */}
                  <td className="py-3.5 px-3 text-right">
                    <Link
                      href={`/assets/${eq.id}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-[#ff5a24] hover:text-black transition-colors"
                    >
                      <span>Detail</span>
                      <ChevronRight className="size-3.5" />
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredList.length === 0 && (
          <div className="py-12 text-center text-xs text-[#7a7a7a]">
            No equipment records matched the selected query.
          </div>
        )}
      </div>
    </GlassCard>
  );
}
