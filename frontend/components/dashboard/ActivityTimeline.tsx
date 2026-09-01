import React from "react";
import Link from "next/link";
import { History, ArrowUpRight, CheckCircle2, UserCheck, ShieldAlert, ArrowLeftRight } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { AuditEvent } from "@/types";

interface ActivityTimelineProps {
  events?: AuditEvent[];
}

const DEFAULT_EVENTS: Array<{
  id: number;
  event_type: string;
  equipment_id: string;
  actor: string;
  timestamp: string;
  details: string;
}> = [
  {
    id: 1,
    event_type: "ALERT_CREATED",
    equipment_id: "EQX1001",
    actor: "Status Engine",
    timestamp: "8 hours ago",
    details: "Low utilization threshold flag triggered (11.2% active).",
  },
  {
    id: 2,
    event_type: "CHECKOUT",
    equipment_id: "EQX1002",
    actor: "Yard Logistics",
    timestamp: "2 days ago",
    details: "Delivered to Northside Logistics Hub staging area.",
  },
  {
    id: 3,
    event_type: "CHECKIN",
    equipment_id: "EQX1007",
    actor: "Marcus Vance",
    timestamp: "3 days ago",
    details: "Returned from Highland Medical Center. Full inspection passed.",
  },
  {
    id: 4,
    event_type: "CHECKOUT",
    equipment_id: "EQX1001",
    actor: "System Dispatch",
    timestamp: "5 days ago",
    details: "Dispatched to Metro Tunnel Extension for excavation.",
  },
];

export function ActivityTimeline({ events }: ActivityTimelineProps) {
  const getEventIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case "ALERT_CREATED":
        return <ShieldAlert className="size-3.5 text-[#ff5a24]" />;
      case "CHECKOUT":
        return <ArrowLeftRight className="size-3.5 text-blue-600" />;
      case "CHECKIN":
        return <CheckCircle2 className="size-3.5 text-emerald-600" />;
      default:
        return <UserCheck className="size-3.5 text-[#7a7a7a]" />;
    }
  };

  return (
    <GlassCard variant="light" className="p-7 flex flex-col justify-between h-full">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="size-4 text-[#ff5a24]" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
              Fleet Activity Timeline
            </h3>
          </div>
          <span className="text-xs font-mono text-[#7a7a7a]">Audit Trail</span>
        </div>
        <p className="text-xs text-[#6a6a6a] mt-1">
          Immutable event log of rental handoffs and telemetry flags
        </p>
      </div>

      {/* Vertical Timeline */}
      <div className="mt-6 space-y-5 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-black/10">
        {DEFAULT_EVENTS.map((event) => (
          <div key={event.id} className="relative flex items-start gap-4 pl-1">
            {/* Timeline Icon Node */}
            <div className="size-7 rounded-full border border-black/10 bg-white grid place-items-center shadow-sm shrink-0 z-10">
              {getEventIcon(event.event_type)}
            </div>

            {/* Event Description */}
            <div className="flex-1 rounded-xl border border-black/5 bg-white/60 p-3 shadow-xs">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Link
                    href={`/assets/${event.equipment_id}`}
                    className="font-bold text-[#ff5a24] hover:underline"
                  >
                    {event.equipment_id}
                  </Link>
                  <span className="font-mono text-[10px] uppercase font-semibold text-[#555]">
                    {event.event_type}
                  </span>
                </div>
                <span className="text-[10px] text-[#888] font-mono">{event.timestamp}</span>
              </div>

              <p className="text-xs text-[#333] mt-1 leading-snug">
                {event.details}
              </p>

              <span className="text-[10px] text-[#7a7a7a] mt-1.5 block">
                Actor: <span className="font-medium text-black">{event.actor}</span>
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Link */}
      <div className="mt-4 pt-3 border-t border-black/10 flex items-center justify-between text-xs text-[#6a6a6a]">
        <span>Blockchain Audit Sync</span>
        <span className="text-[#ff5a24] font-medium hover:underline cursor-pointer">
          Audit Timeline Logs →
        </span>
      </div>
    </GlassCard>
  );
}
