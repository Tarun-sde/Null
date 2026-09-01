"use client";

import React, { useState, useEffect } from "react";
import { X, CheckCircle2, AlertCircle, ArrowRight, Loader2, Calendar, MapPin, User } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { StatusBadge } from "../ui/StatusBadge";
import { fetchSites, fetchOperators, checkoutEquipment } from "@/lib/api";
import { Site, Operator, CheckoutResponse } from "@/types";
import { cn } from "@/lib/utils";

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  equipmentId: string;
  equipmentType?: string;
  dailyRate?: number;
  dealer?: string;
  onSuccess?: (res: CheckoutResponse) => void;
}

export function CheckoutModal({
  isOpen,
  onClose,
  equipmentId,
  equipmentType = "Heavy Machinery",
  dailyRate = 400,
  dealer = "Equipment Dealer",
  onSuccess,
}: CheckoutModalProps) {
  const [sites, setSites] = useState<Site[]>([]);
  const [operators, setOperators] = useState<Operator[]>([]);
  const [loadingOptions, setLoadingOptions] = useState(false);

  // Form State
  const [selectedSiteId, setSelectedSiteId] = useState("");
  const [selectedOperatorId, setSelectedOperatorId] = useState("");
  const [dueDate, setDueDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split("T")[0];
  });
  const [conditionNotes, setConditionNotes] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<CheckoutResponse | null>(null);

  useEffect(() => {
    if (!isOpen) {
      setSuccessData(null);
      setErrorMessage(null);
      return;
    }

    const loadOptions = async () => {
      try {
        setLoadingOptions(true);
        const [sitesRes, opsRes] = await Promise.all([
          fetchSites(),
          fetchOperators(),
        ]);
        setSites(sitesRes);
        setOperators(opsRes);
        if (sitesRes.length > 0) setSelectedSiteId(sitesRes[0].id);
        if (opsRes.length > 0) setSelectedOperatorId(opsRes[0].id);
      } catch (err: any) {
        console.error("Failed to load sites/operators:", err);
      } finally {
        setLoadingOptions(false);
      }
    };

    loadOptions();
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSiteId || !selectedOperatorId || !dueDate) {
      setErrorMessage("Please complete all required deployment fields.");
      return;
    }

    try {
      setSubmitting(true);
      setErrorMessage(null);
      const dueDateTime = new Date(`${dueDate}T18:00:00Z`).toISOString();

      const res = await checkoutEquipment({
        equipment_id: equipmentId,
        site_id: selectedSiteId,
        operator_id: selectedOperatorId,
        due_at: dueDateTime,
        daily_rate: dailyRate,
        condition_notes: conditionNotes || "Dispatched in verified operational order.",
        actor: "Operator",
      });

      setSuccessData(res);
      if (onSuccess) {
        onSuccess(res);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute equipment checkout.");
    } finally {
      setSubmitting(false);
    }
  };

  const selectedSite = sites.find((s) => s.id === selectedSiteId);
  const selectedOperator = operators.find((o) => o.id === selectedOperatorId);

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
            <span className="size-2 rounded-full bg-[#ff5a24] animate-pulse" />
            <span className="text-xs font-semibold uppercase tracking-wider text-[#7a7a7a]">
              DEPLOYMENT CONTRACT
            </span>
          </div>

          <h2
            className="text-2xl font-medium tracking-tight text-black"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            Check Out Equipment
          </h2>

          {/* Equipment Asset Pill */}
          <div className="my-4 p-3.5 rounded-xl border border-black/10 bg-black/[0.02] flex items-center justify-between text-xs">
            <div>
              <span className="font-bold text-base text-black block">{equipmentId}</span>
              <span className="text-[#666]">{equipmentType} • {dealer}</span>
            </div>
            <div className="text-right">
              <span className="font-mono font-bold text-sm text-black block">${dailyRate}/day</span>
              <StatusBadge status="UNASSIGNED" size="sm" />
            </div>
          </div>

          {/* Success State */}
          {successData ? (
            <div className="py-6 text-center space-y-4">
              <div className="size-12 rounded-full bg-emerald-100 text-emerald-600 grid place-items-center mx-auto">
                <CheckCircle2 className="size-6" />
              </div>
              <h3 className="text-lg font-bold text-black">Equipment Checked Out Successfully</h3>
              <div className="p-4 rounded-xl bg-black/[0.03] border border-black/5 text-xs text-left space-y-2">
                <div className="flex justify-between">
                  <span className="text-[#7a7a7a]">Deployed Site:</span>
                  <span className="font-semibold text-black">{successData.rental.site?.name || selectedSiteId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#7a7a7a]">Assigned Operator:</span>
                  <span className="font-semibold text-black">{successData.rental.operator?.name || selectedOperatorId}</span>
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
            /* Checkout Form */
            <form onSubmit={handleSubmit} className="space-y-4">
              {errorMessage && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
                  <AlertCircle className="size-4 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Site Selection */}
              <div>
                <label className="block text-xs font-semibold text-black mb-1.5 flex items-center gap-1.5">
                  <MapPin className="size-3.5 text-[#ff5a24]" />
                  <span>Destination Construction Site *</span>
                </label>
                <select
                  value={selectedSiteId}
                  onChange={(e) => setSelectedSiteId(e.target.value)}
                  disabled={loadingOptions || submitting}
                  className="w-full rounded-xl border border-black/15 bg-white px-3.5 py-2.5 text-xs text-black focus:outline-none focus:ring-1 focus:ring-[#ff5a24]"
                >
                  {sites.map((site) => (
                    <option key={site.id} value={site.id}>
                      {site.name} ({site.id}) — {site.location}
                    </option>
                  ))}
                </select>
              </div>

              {/* Operator Selection */}
              <div>
                <label className="block text-xs font-semibold text-black mb-1.5 flex items-center gap-1.5">
                  <User className="size-3.5 text-[#ff5a24]" />
                  <span>Certified Heavy Operator *</span>
                </label>
                <select
                  value={selectedOperatorId}
                  onChange={(e) => setSelectedOperatorId(e.target.value)}
                  disabled={loadingOptions || submitting}
                  className="w-full rounded-xl border border-black/15 bg-white px-3.5 py-2.5 text-xs text-black focus:outline-none focus:ring-1 focus:ring-[#ff5a24]"
                >
                  {operators.map((op) => (
                    <option key={op.id} value={op.id}>
                      {op.name} ({op.id})
                    </option>
                  ))}
                </select>
              </div>

              {/* Due Date */}
              <div>
                <label className="block text-xs font-semibold text-black mb-1.5 flex items-center gap-1.5">
                  <Calendar className="size-3.5 text-[#ff5a24]" />
                  <span>Scheduled Return Date *</span>
                </label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  disabled={submitting}
                  className="w-full rounded-xl border border-black/15 bg-white px-3.5 py-2.5 text-xs text-black focus:outline-none focus:ring-1 focus:ring-[#ff5a24]"
                />
              </div>

              {/* Condition Notes */}
              <div>
                <label className="block text-xs font-semibold text-black mb-1.5">
                  Inspection / Dispatch Notes (Optional)
                </label>
                <textarea
                  value={conditionNotes}
                  onChange={(e) => setConditionNotes(e.target.value)}
                  placeholder="e.g. Delivered with full tank and clean cab inspection."
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
                  disabled={submitting || loadingOptions}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#111111] text-white font-semibold text-xs shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:bg-black transition-all disabled:opacity-50"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="size-3.5 animate-spin" />
                      <span>Authorizing Dispatch...</span>
                    </>
                  ) : (
                    <>
                      <span>Confirm Check Out</span>
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
