import React from "react";
import Link from "next/link";
import { Sparkles, DollarSign, ArrowRight, CheckCircle2 } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";

interface RecommendationItem {
  id: string | number;
  equipment_id: string;
  action_type: "RETURN" | "REASSIGN" | "EXTEND" | "ASSIGN" | string;
  recommendation: string;
  confidence: number;
  avoided_cost: number;
  explanation: string;
}

const DEFAULT_RECOMMENDATIONS: RecommendationItem[] = [
  {
    id: "REC-01",
    equipment_id: "EQX1006",
    action_type: "RETURN",
    recommendation: "Immediate Off-Rent Handoff",
    confidence: 0.96,
    avoided_cost: 900,
    explanation: "Overdue scissor lift no longer active in site trade schedule. Eliminates $180/day excess rate.",
  },
  {
    id: "REC-02",
    equipment_id: "EQX1001",
    action_type: "REASSIGN",
    recommendation: "Reassign to Highland Medical Foundation",
    confidence: 0.89,
    avoided_cost: 1350,
    explanation: "Excavator is 88.8% idle at Metro Tunnel. Moving to Highland prevents additional 3-day rental.",
  },
  {
    id: "REC-03",
    equipment_id: "EQX1002",
    action_type: "ASSIGN",
    recommendation: "Assign Operator Devon Cole",
    confidence: 0.94,
    avoided_cost: 650,
    explanation: "Bulldozer sitting in staging. Operator certification matches site safety requirements.",
  },
];

export function RecommendationsPanel() {
  return (
    <GlassCard variant="light" className="p-7 flex flex-col justify-between h-full">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="size-4 text-[#ff5a24]" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
              AI Decision Queue
            </h3>
          </div>
          <span className="text-xs font-mono text-[#ff5a24] font-semibold bg-orange-50 px-2.5 py-0.5 rounded-full border border-[#ff5a24]/30">
            $2,900 Avoidable Cost
          </span>
        </div>
        <p className="text-xs text-[#6a6a6a] mt-1">
          Ranked cost avoidance &amp; fleet optimization recommendations
        </p>
      </div>

      {/* Cards List */}
      <div className="mt-5 space-y-3.5">
        {DEFAULT_RECOMMENDATIONS.map((rec) => (
          <div
            key={rec.id}
            className="rounded-xl border border-black/10 bg-white/70 p-4 shadow-sm hover:shadow-md transition-all group"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <Link
                    href={`/assets/${rec.equipment_id}`}
                    className="font-bold text-xs text-[#ff5a24] hover:underline"
                  >
                    {rec.equipment_id}
                  </Link>
                  <span className="text-xs font-semibold text-black">{rec.recommendation}</span>
                </div>
                <p className="text-xs text-[#555555] mt-1 leading-snug">
                  {rec.explanation}
                </p>
              </div>

              <div className="text-right shrink-0">
                <span className="text-xs font-bold text-emerald-700 block font-mono">
                  +${rec.avoided_cost}
                </span>
                <span className="text-[10px] text-[#7a7a7a] block mt-0.5">
                  {Math.round(rec.confidence * 100)}% Conf.
                </span>
              </div>
            </div>

            {/* Action Bar */}
            <div className="mt-3 pt-2.5 border-t border-black/5 flex items-center justify-between text-xs">
              <span className="text-[11px] text-[#7a7a7a] font-mono uppercase">
                Action: {rec.action_type}
              </span>
              <div className="flex items-center gap-2">
                <button className="px-2.5 py-1 rounded-lg text-[11px] font-medium text-[#7a7a7a] hover:bg-black/5 transition-colors">
                  Dismiss
                </button>
                <button className="px-3 py-1 rounded-lg text-[11px] font-medium bg-[#111111] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] hover:bg-black transition-all">
                  Resolve Action
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Link */}
      <div className="mt-4 pt-3 border-t border-black/10 flex items-center justify-between text-xs text-[#6a6a6a]">
        <span>Decision Engine Synchronized</span>
        <Link href="/actions" className="text-[#ff5a24] font-medium hover:underline">
          View Complete Action Queue →
        </Link>
      </div>
    </GlassCard>
  );
}
