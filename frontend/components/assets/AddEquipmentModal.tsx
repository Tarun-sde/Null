"use client";

import React, { useState } from "react";
import { X, Plus, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { createEquipment } from "@/lib/api";
import { cn } from "@/lib/utils";

interface AddEquipmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const EQUIPMENT_TYPES = [
  "Excavator",
  "Bulldozer",
  "Wheel Loader",
  "Generator",
  "Scissor Lift",
  "Boom Lift",
  "Skid Steer",
  "Crane",
  "Compactor",
  "Forklift",
  "Dump Truck",
  "Concrete Mixer",
  "Other",
];

interface FormState {
  id: string;
  type: string;
  customType: string;
  dealer: string;
  daily_rate: string;
  model: string;
  serial: string;
}

const INITIAL: FormState = {
  id: "",
  type: "",
  customType: "",
  dealer: "",
  daily_rate: "",
  model: "",
  serial: "",
};

export function AddEquipmentModal({ isOpen, onClose, onSuccess }: AddEquipmentModalProps) {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const set = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const val = field === "id" ? e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "") : e.target.value;
    setForm((prev) => ({ ...prev, [field]: val }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
    setServerError(null);
  };

  const validate = (): boolean => {
    const next: typeof errors = {};
    if (!form.id.trim()) next.id = "Equipment ID is required";
    else if (form.id.length < 3) next.id = "ID must be at least 3 characters";

    const effectiveType = form.type === "Other" ? form.customType.trim() : form.type;
    if (!effectiveType) next.type = "Equipment type is required";

    if (!form.dealer.trim()) next.dealer = "Dealer name is required";

    const rate = parseFloat(form.daily_rate);
    if (!form.daily_rate.trim() || isNaN(rate) || rate <= 0)
      next.daily_rate = "Daily rate must be a positive number";

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const effectiveType = form.type === "Other" ? form.customType.trim() : form.type;

    setLoading(true);
    setServerError(null);

    try {
      await createEquipment({
        id: form.id.trim(),
        type: effectiveType,
        dealer: form.dealer.trim(),
        daily_rate: parseFloat(form.daily_rate),
        model: form.model.trim() || undefined,
        serial: form.serial.trim() || undefined,
      });
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setForm(INITIAL);
        onSuccess();
        onClose();
      }, 1200);
    } catch (err: unknown) {
      setServerError(err instanceof Error ? err.message : "Failed to create equipment");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (loading) return;
    setForm(INITIAL);
    setErrors({});
    setServerError(null);
    setSuccess(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div
        className="relative w-full max-w-lg rounded-2xl border border-black/10 shadow-[0_32px_80px_rgba(0,0,0,0.16),inset_0_1px_0_rgba(255,255,255,0.9)] overflow-hidden"
        style={{ background: "rgba(255,255,255,0.95)", backdropFilter: "blur(20px)" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-7 pt-6 pb-5 border-b border-black/10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="size-2 bg-[#ff5a24]" />
              <span className="text-xs font-semibold uppercase tracking-wider text-[#6a6a6a]">
                FLEET MANAGEMENT
              </span>
            </div>
            <h2
              className="text-xl font-medium text-black tracking-tight"
              style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
            >
              Register New Equipment
            </h2>
          </div>
          <button
            onClick={handleClose}
            disabled={loading}
            className="rounded-xl p-2 text-[#7a7a7a] hover:bg-black/5 hover:text-black transition-all"
            aria-label="Close modal"
          >
            <X className="size-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-7 py-5 space-y-4">
          {/* Equipment ID */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5">
              Equipment ID <span className="text-[#ff5a24]">*</span>
            </label>
            <input
              id="new-equipment-id"
              type="text"
              value={form.id}
              onChange={set("id")}
              placeholder="e.g. EQX1008"
              maxLength={20}
              className={cn(
                "w-full rounded-xl border bg-white/80 px-4 py-2.5 text-sm font-mono text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 transition-all",
                errors.id
                  ? "border-red-400 focus:ring-red-200"
                  : "border-black/10 focus:ring-[#ff5a24]/25 focus:border-[#ff5a24]/40"
              )}
            />
            {errors.id && (
              <p className="mt-1 text-xs text-red-600">{errors.id}</p>
            )}
            <p className="mt-1 text-[11px] text-[#9a9a9a]">
              Unique identifier. Also used as the QR scan code.
            </p>
          </div>

          {/* Type */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5">
              Equipment Type <span className="text-[#ff5a24]">*</span>
            </label>
            <select
              id="new-equipment-type"
              value={form.type}
              onChange={set("type")}
              className={cn(
                "w-full rounded-xl border bg-white/80 px-4 py-2.5 text-sm text-black focus:bg-white focus:outline-none focus:ring-2 transition-all",
                errors.type
                  ? "border-red-400 focus:ring-red-200"
                  : "border-black/10 focus:ring-[#ff5a24]/25 focus:border-[#ff5a24]/40"
              )}
            >
              <option value="">Select type…</option>
              {EQUIPMENT_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            {form.type === "Other" && (
              <input
                type="text"
                value={form.customType}
                onChange={set("customType")}
                placeholder="Specify equipment type"
                className="mt-2 w-full rounded-xl border border-black/10 bg-white/80 px-4 py-2.5 text-sm text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#ff5a24]/25 focus:border-[#ff5a24]/40 transition-all"
              />
            )}
            {errors.type && (
              <p className="mt-1 text-xs text-red-600">{errors.type}</p>
            )}
          </div>

          {/* Dealer + Daily Rate side by side */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5">
                Dealer <span className="text-[#ff5a24]">*</span>
              </label>
              <input
                id="new-equipment-dealer"
                type="text"
                value={form.dealer}
                onChange={set("dealer")}
                placeholder="e.g. Tata Hitachi / JCB India / BEML"
                className={cn(
                  "w-full rounded-xl border bg-white/80 px-4 py-2.5 text-sm text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 transition-all",
                  errors.dealer
                    ? "border-red-400 focus:ring-red-200"
                    : "border-black/10 focus:ring-[#ff5a24]/25 focus:border-[#ff5a24]/40"
                )}
              />
              {errors.dealer && (
                <p className="mt-1 text-xs text-red-600">{errors.dealer}</p>
              )}
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5">
                Daily Rate (INR ₹) <span className="text-[#ff5a24]">*</span>
              </label>
              <input
                id="new-equipment-rate"
                type="number"
                min="100"
                step="100"
                value={form.daily_rate}
                onChange={set("daily_rate")}
                placeholder="18500"
                className={cn(
                  "w-full rounded-xl border bg-white/80 px-4 py-2.5 text-sm text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 transition-all",
                  errors.daily_rate
                    ? "border-red-400 focus:ring-red-200"
                    : "border-black/10 focus:ring-[#ff5a24]/25 focus:border-[#ff5a24]/40"
                )}
              />
              {errors.daily_rate && (
                <p className="mt-1 text-xs text-red-600">{errors.daily_rate}</p>
              )}
            </div>
          </div>

          {/* Model + Serial — optional */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5">
                Model <span className="text-[#9a9a9a] font-normal normal-case">(optional)</span>
              </label>
              <input
                id="new-equipment-model"
                type="text"
                value={form.model}
                onChange={set("model")}
                placeholder="e.g. CAT 320 GC"
                className="w-full rounded-xl border border-black/10 bg-white/80 px-4 py-2.5 text-sm text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#ff5a24]/25 focus:border-[#ff5a24]/40 transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5">
                Serial No. <span className="text-[#9a9a9a] font-normal normal-case">(optional)</span>
              </label>
              <input
                id="new-equipment-serial"
                type="text"
                value={form.serial}
                onChange={set("serial")}
                placeholder="e.g. CAT320-9942"
                className="w-full rounded-xl border border-black/10 bg-white/80 px-4 py-2.5 text-sm text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#ff5a24]/25 focus:border-[#ff5a24]/40 transition-all"
              />
            </div>
          </div>

          {/* Server error */}
          {serverError && (
            <div className="flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
              <AlertCircle className="size-4 shrink-0 text-red-500 mt-0.5" />
              <span>{serverError}</span>
            </div>
          )}

          {/* Success */}
          {success && (
            <div className="flex items-center gap-2.5 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-700">
              <CheckCircle2 className="size-4 text-emerald-600" />
              <span>Equipment registered successfully!</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2.5 rounded-xl text-xs font-medium text-[#555] hover:bg-black/5 hover:text-black transition-all"
            >
              Cancel
            </button>
            <button
              id="add-equipment-submit"
              type="submit"
              disabled={loading || success}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#111111] text-white text-xs font-semibold shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:bg-black transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <><Loader2 className="size-4 animate-spin" /><span>Registering…</span></>
              ) : success ? (
                <><CheckCircle2 className="size-4 text-emerald-400" /><span>Registered!</span></>
              ) : (
                <><Plus className="size-4 text-[#ff5a24]" /><span>Register Equipment</span></>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
