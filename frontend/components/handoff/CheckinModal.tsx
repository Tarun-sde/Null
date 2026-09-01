"use client";

import React, { useState } from "react";
import { X, CheckCircle2, AlertCircle, ArrowRight, Loader2, ShieldCheck } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { StatusBadge } from "../ui/StatusBadge";
import { checkinEquipment } from "@/lib/api";
import { CheckinResponse } from "@/types";
import { cn } from "@/lib/utils";

interface CheckinModalProps {
  isOpen: boolean;
  onClose: () => void;
  equipmentId: string;
  equipmentType?: string;
  currentSiteName?: string;
  currentOperatorName?: string;
  currentStatus?: string;
  onSuccess?: (res: CheckinResponse) => void;
}

const CONDITIONS = [
  { value: "Good", label: "Good Condition", desc: "Clean return, full operational readiness" },
  { value: "Minor Damage", label: "Minor Scuffs / Wear", desc: "Cosmetic wear, standard operating condition" },
  { value: "Needs Inspection", label: "Needs Mechanical Inspection", desc: "Diagnostic check recommended" },
  { value: "Damaged", label: "Damaged / Maintenance Required", desc: "Requires yard mechanic servicing" },
];

export function CheckinModal({
  isOpen,
  onClose,
  equipmentId,
  equipmentType = "Heavy Machinery",
  currentSiteName = "Current Site",
  currentOperatorName = "Assigned Operator",
  currentStatus = "ACTIVE",
  onSuccess,
}: CheckinModalProps) {
  const [condition, setCondition] = useState("Good");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<CheckinResponse | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setErrorMessage(null);
      const res = await checkinEquipment({
        equipment_id: equipmentId,
        condition,
        notes: notes || "Equipment inspected and received into yard inventory.",
        actor: "Operator",
      });

      setSuccessData(res);
      if (onSuccess) {
        onSuccess(res);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute equipment check-in.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in-reveal">
      <div className="relative w-full max-w-lg">
        <GlassCard className="p-7 relative overflow-hidden bg-white/95">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-5 right-5 grid size-8 place-items-center rounded-lg text-[#7a7a7a] hover:bg-black/5 hover:text-black transition-colors"
          >
            <X className="size-4" />
          </button>

          {/* Modal Header */}
          <div className="flex items-center gap-2 mb-1">
            <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold uppercase tracking-wider text-[#7a7a7a]">
              RETURN / OFF-RENT HANDOFF
            </span>
          </div>

          <h2
            className="text-2xl font-medium tracking-tight text-black"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            Check In Equipment
          </h2>

          {/* Equipment Asset Pill */}
          <div className="my-4 p-3.5 rounded-xl border border-black/10 bg-black/[0.02] flex items-center justify-between text-xs">
            <div>
              <span className="font-bold text-base text-black block">{equipmentId}</span>
              <span className="text-[#666]">{equipmentType}</span>
              <span className="text-[11px] text-[#888] block mt-0.5">
                Site: {currentSiteName} • Operator: {currentOperatorName}
              </span>
            </div>
            <div className="text-right">
              <StatusBadge status={currentStatus} size="sm" />
            </div>
          </div>

          {/* Success State */}
          {successData ? (
            <div className="py-6 text-center space-y-4">
              <div className="size-12 rounded-full bg-emerald-100 text-emerald-600 grid place-items-center mx-auto">
                <CheckCircle2 className="size-6" />
              </div>
              <h3 className="text-lg font-bold text-black">Equipment Checked In Successfully</h3>
              <div className="p-4 rounded-xl bg-black/[0.03] border border-black/5 text-xs text-left space-y-2">
                <div className="flex justify-between">
                  <span className="text-[#7a7a7a]">Asset ID:</span>
                  <span className="font-semibold text-black">{equipmentId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#7a7a7a]">Return Condition:</span>
                  <span className="font-semibold text-black">{condition}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#7a7a7a]">Recalculated Status:</span>
                  <StatusBadge status={successData.status} size="sm" />
                </div>
              </div>

              <div className="pt-3 flex items-center justify-end gap-3">
                <button
                  onClick={onClose}
                  className="w-full py-2.5 rounded-xl bg-[#111111] text-white font-medium text-xs hover:bg-black transition-all shadow-sm"
                >
                  Done
                </button>
              </div>
            </div>
          ) : (
            /* Checkin Form */
            <form onSubmit={handleSubmit} className="space-y-4">
              {errorMessage && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
                  <AlertCircle className="size-4 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Condition Options */}
              <div>
                <label className="block text-xs font-semibold text-black mb-2 flex items-center gap-1.5">
                  <ShieldCheck className="size-3.5 text-[#ff5a24]" />
                  <span>Return Equipment Condition *</span>
                </label>
                <div className="space-y-2">
                  {CONDITIONS.map((c) => (
                    <label
                      key={c.value}
                      className={cn(
                        "flex items-start gap-3 p-3 rounded-xl border text-xs cursor-pointer transition-all",
                        condition === c.value
                          ? "border-black bg-black/[0.03] text-black font-medium shadow-xs"
                          : "border-black/10 bg-white text-[#555] hover:bg-black/[0.01]"
                      )}
                    >
                      <input
                        type="radio"
                        name="condition"
                        value={c.value}
                        checked={condition === c.value}
                        onChange={(e) => setCondition(e.target.value)}
                        className="mt-0.5 accent-[#ff5a24]"
                      />
                      <div>
                        <span className="font-semibold text-black block">{c.label}</span>
                        <span className="text-[11px] text-[#7a7a7a] block mt-0.5">{c.desc}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <label className="block text-xs font-semibold text-black mb-1.5">
                  Return Inspection Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Returned to central yard, fuel replenished to 100%, no structural faults detected."
                  rows={2}
                  disabled={submitting}
                  className="w-full rounded-xl border border-black/15 bg-white px-3.5 py-2 text-xs text-black focus:outline-none focus:ring-1 focus:ring-[#ff5a24]"
                />
              </div>

              {/* Action Buttons */}
              <div className="pt-3 flex items-center justify-end gap-3 border-t border-black/10">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={submitting}
                  className="px-4 py-2.5 rounded-xl text-xs font-medium text-[#7a7a7a] hover:bg-black/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#111111] text-white font-semibold text-xs shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:bg-black transition-all disabled:opacity-50"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="size-3.5 animate-spin" />
                      <span>Processing Return...</span>
                    </>
                  ) : (
                    <>
                      <span>Confirm Check In</span>
                      <ArrowRight className="size-3.5 text-[#ff5a24]" />
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </GlassCard>
      </div>
    </div>
  );
}
