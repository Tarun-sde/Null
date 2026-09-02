import React from "react";
import Link from "next/link";
import { ArrowUpRight, Fuel, Gauge, MapPin, User } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { StatusBadge } from "../ui/StatusBadge";
import { EquipmentListItem } from "@/types";
import { cn, formatDayRate } from "@/lib/utils";

interface AssetCardProps {
  equipment: EquipmentListItem;
}

export function AssetCard({ equipment }: AssetCardProps) {
  const model = (equipment.metadata_json as { model?: string } | null)?.model || "Standard Heavy Spec";
  const utilPct = Math.round(equipment.utilization_rate * 100);
  const engineHours = equipment.latest_telemetry?.engine_hours || 0;
  const idleHours = equipment.latest_telemetry?.idle_hours || 0;
  const fuelPct = equipment.latest_telemetry?.fuel_pct ?? 100;

  return (
    <GlassCard isHoverable className="p-6 flex flex-col justify-between">
      <div>
        {/* Card Header */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-black">{equipment.id}</span>
              <span className="text-xs font-semibold text-[#7a7a7a]">
                {formatDayRate(equipment.daily_rate)}
              </span>
            </div>
            <h4 className="text-sm font-semibold text-black mt-0.5">{equipment.type}</h4>
            <p className="text-xs text-[#7a7a7a]">{model} • {equipment.dealer}</p>
          </div>
          <StatusBadge status={equipment.status} size="sm" />
        </div>

        {/* Details Grid */}
        <div className="mt-5 space-y-2.5 pt-4 border-t border-black/10 text-xs">
          {/* Site */}
          <div className="flex items-center gap-2 text-[#444]">
            <MapPin className="size-3.5 text-[#ff5a24] shrink-0" />
            <span className="truncate">{equipment.site?.name || "Yard Staging Area"}</span>
          </div>

          {/* Operator */}
          <div className="flex items-center gap-2 text-[#444]">
            <User className="size-3.5 text-[#7a7a7a] shrink-0" />
            <span className="truncate">{equipment.operator?.name || "Unassigned Operator"}</span>
          </div>

          {/* Telemetry Readout */}
          <div className="flex items-center justify-between pt-1 text-[11px] text-[#666]">
            <span className="flex items-center gap-1">
              <Gauge className="size-3 text-[#ff5a24]" />
              {engineHours}h engine ({idleHours}h idle)
            </span>
            <span className="flex items-center gap-1 font-mono">
              <Fuel className="size-3 text-[#7a7a7a]" />
              {fuelPct}%
            </span>
          </div>

          {/* Utilization Progress */}
          <div className="space-y-1 pt-1">
            <div className="flex items-center justify-between text-[10px] text-[#7a7a7a]">
              <span>Utilization Efficiency</span>
              <span className="font-bold text-black">{utilPct}%</span>
            </div>
            <div className="h-1.5 w-full bg-black/10 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  utilPct < 20 ? "bg-amber-500" : "bg-[#ff5a24]"
                )}
                style={{ width: `${Math.min(100, Math.max(5, utilPct))}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Card Action Link */}
      <div className="mt-6 pt-3 border-t border-black/10 flex items-center justify-between">
        <span className="text-[11px] text-[#7a7a7a] font-mono">
          {equipment.current_rental ? "Under Contract" : "Standby"}
        </span>
        <Link
          href={`/assets/${equipment.id}`}
          className="inline-flex items-center gap-1 text-xs font-bold text-[#ff5a24] hover:text-black transition-colors"
        >
          <span>View Telemetry</span>
          <ArrowUpRight className="size-3.5" />
        </Link>
      </div>
    </GlassCard>
  );
}
