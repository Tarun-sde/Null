import React from "react";
import Link from "next/link";
import { AlertTriangle, ArrowUpRight, CheckCircle2, Clock } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { Alert } from "@/types";
import { cn } from "@/lib/utils";

interface AlertsPanelProps {
  alerts?: (Alert | {
    id: number | string;
    equipment_id: string;
    alert_type: string;
    severity: string;
    message: string;
    created_at?: string;
    timestamp?: string;
    action_label?: string;
  })[];
}

export function AlertsPanel({ alerts = [] }: AlertsPanelProps) {
  const formatTimeAgo = (dateStr?: string, fallback = "Recently") => {
    if (!dateStr) return fallback;
    try {
      const d = new Date(dateStr);
      const now = new Date();
      const diffMs = now.getTime() - d.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return "Just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays}d ago`;
    } catch {
      return fallback;
    }
  };

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
        {alerts.length === 0 ? (
          <div className="py-8 text-center text-xs text-white/50">
            <CheckCircle2 className="size-6 text-emerald-400 mx-auto mb-2" />
            No active anomalies detected across the fleet.
          </div>
        ) : (
          alerts.map((alert) => {
            const style = getSeverityStyle(alert.severity);
            const timeDisplay = alert.created_at
              ? formatTimeAgo(alert.created_at)
              : (alert as any).timestamp || "Recently";

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
                        {timeDisplay}
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
          })
        )}
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
