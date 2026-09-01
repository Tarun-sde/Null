import React from "react";
import Link from "next/link";
import { AlertTriangle, ArrowUpRight, CheckCircle2, Clock } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { cn } from "@/lib/utils";

interface AlertItem {
  id: number | string;
  equipment_id: string;
  alert_type: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  message: string;
  timestamp: string;
  action_label?: string;
}

interface AlertsPanelProps {
  alerts?: AlertItem[];
}

const DEFAULT_ALERTS: AlertItem[] = [
  {
    id: 1,
    equipment_id: "EQX1002",
    alert_type: "MISSING_ASSIGNMENT",
    severity: "CRITICAL",
    message: "Bulldozer checked out at Northside Logistics Hub without certified operator assignment.",
    timestamp: "12m ago",
    action_label: "Assign Operator",
  },
  {
    id: 2,
    equipment_id: "EQX1001",
    alert_type: "LOW_UTILIZATION",
    severity: "HIGH",
    message: "Excavator idle hours (14.2h) exceed 8h threshold. Fleet utilization is only 11.2%.",
    timestamp: "2h ago",
    action_label: "Reassign / Return",
  },
  {
    id: 3,
    equipment_id: "EQX1006",
    alert_type: "OVERDUE",
    severity: "HIGH",
    message: "Scissor Lift rental is 48h past due return date. Rate surcharge active ($180/day).",
    timestamp: "2d ago",
    action_label: "Initiate Return",
  },
  {
    id: 4,
    equipment_id: "EQX1004",
    alert_type: "DUE_SOON",
    severity: "MEDIUM",
    message: "Generator rental expires in 20 hours. Confirm site release or rental extension.",
    timestamp: "4h ago",
    action_label: "Extend Rental",
  },
];

export function AlertsPanel({ alerts = DEFAULT_ALERTS }: AlertsPanelProps) {
  const getSeverityStyle = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return {
          stripe: "bg-red-500",
          badge: "bg-red-500/20 text-red-300 border-red-500/30",
          dot: "bg-red-500",
        };
      case "HIGH":
        return {
          stripe: "bg-[#ff5a24]",
          badge: "bg-[#ff5a24]/20 text-[#ff8a5c] border-[#ff5a24]/30",
          dot: "bg-[#ff5a24]",
        };
      case "MEDIUM":
        return {
          stripe: "bg-amber-500",
          badge: "bg-amber-500/20 text-amber-300 border-amber-500/30",
          dot: "bg-amber-500",
        };
      default:
        return {
          stripe: "bg-slate-500",
          badge: "bg-slate-500/20 text-slate-300 border-slate-500/30",
          dot: "bg-slate-400",
        };
    }
  };

  return (
    <GlassCard variant="dark" className="p-7 flex flex-col justify-between h-full">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="size-4 text-[#ff5a24]" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-white">
              Urgent Anomaly Alerts
            </h3>
          </div>
          <span className="text-xs font-mono text-white/60">{alerts.length} Open</span>
        </div>
        <p className="text-xs text-white/50 mt-1">
          Algorithmic fleet exceptions requiring operator triage
        </p>
      </div>

      {/* Alerts List */}
      <div className="mt-5 space-y-3">
        {alerts.map((alert) => {
          const style = getSeverityStyle(alert.severity);
          return (
            <div
              key={alert.id}
              className="relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:bg-white/10 group"
            >
              {/* Left Severity Stripe */}
              <div className={cn("absolute left-0 top-0 bottom-0 w-1", style.stripe)} />

              <div className="flex items-start justify-between gap-3 pl-1">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/assets/${alert.equipment_id}`}
                      className="font-bold text-white text-xs hover:text-[#ff5a24] transition-colors flex items-center gap-1"
                    >
                      <span>{alert.equipment_id}</span>
                      <ArrowUpRight className="size-3 text-white/40 group-hover:text-[#ff5a24]" />
                    </Link>

                    <span
                      className={cn(
                        "text-[10px] px-2 py-0.5 rounded-full font-mono uppercase font-semibold border",
                        style.badge
                      )}
                    >
                      {alert.severity}
                    </span>

                    <span className="text-[10px] text-white/40 flex items-center gap-1 font-mono">
                      <Clock className="size-3" />
                      {alert.timestamp}
                    </span>
                  </div>

                  <p className="text-xs text-white/80 leading-snug pt-0.5">
                    {alert.message}
                  </p>
                </div>

                {alert.action_label && (
                  <button className="shrink-0 rounded-lg border border-white/15 bg-white/10 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-[#ff5a24] hover:border-[#ff5a24] transition-all whitespace-nowrap">
                    {alert.action_label}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Link */}
      <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-xs text-white/60">
        <span>Anomaly Engine Active</span>
        <span className="text-[#ff5a24] font-medium hover:underline cursor-pointer">
          View All Anomaly Signals →
        </span>
      </div>
    </GlassCard>
  );
}
