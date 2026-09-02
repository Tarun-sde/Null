"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  QrCode,
  Camera,
  Search,
  ArrowRight,
  AlertCircle,
  Truck,
  MapPin,
  User,
  DollarSign,
  Loader2,
  ShieldCheck,
} from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { GlassCard } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { CheckoutModal } from "@/components/handoff/CheckoutModal";
import { CheckinModal } from "@/components/handoff/CheckinModal";
import { fetchEquipmentDetail } from "@/lib/api";
import { EquipmentDetail } from "@/types";
import { getErrorMessage, formatDayRate } from "@/lib/utils";

export default function ScanPage() {
  const [manualId, setManualId] = useState("");
  const [identifiedAsset, setIdentifiedAsset] = useState<EquipmentDetail | null>(null);
  const [identifying, setIdentifying] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);

  // Camera Scanner State
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const qrRegionId = "html5qr-code-full-region";
  const scannerRef = useRef<import("html5-qrcode").Html5Qrcode | null>(null);

  // Modal State
  const [checkoutModalOpen, setCheckoutModalOpen] = useState(false);
  const [checkinModalOpen, setCheckinModalOpen] = useState(false);

  const lookupEquipment = async (idToLookup: string) => {
    const cleanId = idToLookup.trim().toUpperCase();
    if (!cleanId) return;

    try {
      setIdentifying(true);
      setLookupError(null);
      const detail = await fetchEquipmentDetail(cleanId);
      setIdentifiedAsset(detail);
      setManualId(cleanId);
    } catch (err: unknown) {
      console.info("Equipment lookup rejected:", err);
      setIdentifiedAsset(null);
      if (getErrorMessage(err, "") === "NOT_FOUND") {
        setLookupError(`Equipment asset "${cleanId}" was not found in the fleet registry.`);
      } else {
        setLookupError(getErrorMessage(err, "Failed to communicate with fleet backend."));
      }
    } finally {
      setIdentifying(false);
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    lookupEquipment(manualId);
  };

  // HTML5 QR Code Scanner initializer
  const startScanner = async () => {
    setCameraError(null);
    setCameraActive(true);

    try {
      const { Html5Qrcode } = await import("html5-qrcode");
      if (!scannerRef.current) {
        scannerRef.current = new Html5Qrcode(qrRegionId);
      }

      await scannerRef.current.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
        },
        (decodedText: string) => {
          // Success callback
          stopScanner();
          lookupEquipment(decodedText);
        },
        () => {
          // Frame error (ignore normal scanning frames)
        }
      );
    } catch (err: unknown) {
      console.warn("Camera init failed:", err);
      setCameraError(
        "Camera stream unavailable or permissions denied. Please use manual ID entry."
      );
      setCameraActive(false);
    }
  };

  const stopScanner = async () => {
    if (scannerRef.current && scannerRef.current.isScanning) {
      try {
        await scannerRef.current.stop();
      } catch {
        // Ignore
      }
    }
    setCameraActive(false);
  };

  useEffect(() => {
    return () => {
      stopScanner();
    };
  }, []);

  const hasActiveRental = Boolean(
    identifiedAsset?.current_rental && !identifiedAsset.current_rental.checked_in_at
  );

  return (
    <AppShell>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5">
          <span className="size-2 bg-[#ff5a24]" />
          <span>FIELD OPERATIONS TERMINAL</span>
        </div>
        <h1
          className="text-3xl sm:text-4xl lg:text-5xl font-medium tracking-tight text-black"
          style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
        >
          Equipment Handoff
        </h1>
        <p className="mt-1.5 text-sm text-[#6a6a6a] max-w-xl">
          Scan equipment QR code or enter asset identifier to initiate verified dispatch check-out or return check-in.
        </p>
      </div>

      <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-8 items-start mb-12">
        {/* Left: QR Scanner & Manual Input Terminal */}
        <div className="space-y-6">
          <GlassCard className="p-7 relative overflow-hidden">
            {/* Viewfinder Header */}
            <div className="flex items-center justify-between pb-4 border-b border-black/10">
              <div className="flex items-center gap-2">
                <QrCode className="size-4 text-[#ff5a24]" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
                  Optical QR Viewfinder
                </h3>
              </div>
              <span className="text-[11px] font-mono text-[#7a7a7a]">
                ISO 18004 Engine
              </span>
            </div>

            {/* Viewfinder Box */}
            <div className="my-6 relative min-h-64 rounded-2xl border border-black/15 bg-[#eae7df] overflow-hidden flex flex-col items-center justify-center p-4">
              {/* HTML5 QR Code Mount Node */}
              <div id={qrRegionId} className="w-full max-w-sm rounded-xl overflow-hidden" />

              {!cameraActive && (
                <div className="text-center p-6 space-y-3 z-10">
                  <div className="size-14 rounded-2xl bg-white/80 border border-black/10 grid place-items-center mx-auto shadow-sm text-black">
                    <Camera className="size-6 text-[#ff5a24]" />
                  </div>
                  <div>
                    <p className="font-semibold text-black text-sm">Optical Camera Inactive</p>
                    <p className="text-xs text-[#6a6a6a] max-w-xs mt-1">
                      Activate device optical camera or use manual identifier input below.
                    </p>
                  </div>
                  <button
                    onClick={startScanner}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#111111] text-white font-medium text-xs shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:bg-black transition-all"
                  >
                    <Camera className="size-3.5 text-[#ff5a24]" />
                    <span>Launch Camera Scanner</span>
                  </button>
                </div>
              )}

              {cameraActive && (
                <button
                  onClick={stopScanner}
                  className="mt-4 px-4 py-2 rounded-lg bg-black/80 text-white text-xs font-medium backdrop-blur shadow-md hover:bg-black transition-colors"
                >
                  Stop Camera
                </button>
              )}

              {cameraError && (
                <div className="mt-4 p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-center gap-2">
                  <AlertCircle className="size-4 shrink-0 text-amber-600" />
                  <span>{cameraError}</span>
                </div>
              )}
            </div>

            {/* Manual ID Input Fallback */}
            <div className="pt-4 border-t border-black/10">
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-2">
                Or Enter Equipment ID Manually
              </label>

              <form onSubmit={handleManualSubmit} className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-[#7a7a7a]" />
                  <input
                    type="text"
                    value={manualId}
                    onChange={(e) => setManualId(e.target.value.toUpperCase())}
                    placeholder="e.g. EQX1007, EQX1001..."
                    className="w-full rounded-xl border border-black/15 bg-white/80 pl-10 pr-4 py-2.5 text-xs text-black font-mono placeholder:text-[#8a8a8a] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#ff5a24]"
                  />
                </div>
                <button
                  type="submit"
                  disabled={identifying || !manualId.trim()}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#111111] text-white text-xs font-semibold shadow-sm hover:bg-black transition-all disabled:opacity-50"
                >
                  {identifying ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <>
                      <span>Identify</span>
                      <ArrowRight className="size-3.5 text-[#ff5a24]" />
                    </>
                  )}
                </button>
              </form>

              {/* Sample Quick Asset Chips */}
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-[#7a7a7a]">
                <span>Quick Select:</span>
                {["EQX1007", "EQX1001", "EQX1002", "EQX1004", "EQX1006"].map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => {
                      setManualId(chip);
                      lookupEquipment(chip);
                    }}
                    className="font-mono text-[11px] px-2.5 py-1 rounded-lg border border-black/10 bg-white/60 text-black hover:bg-white hover:border-black/30 transition-all"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Right: Identified Equipment Verification Card */}
        <div>
          {identifying ? (
            <GlassCard className="p-8 text-center space-y-4">
              <Loader2 className="size-8 text-[#ff5a24] animate-spin mx-auto" />
              <p className="text-xs text-[#6a6a6a]">Querying fleet registry telemetry...</p>
            </GlassCard>
          ) : lookupError ? (
            <GlassCard className="p-8 text-center space-y-3">
              <AlertCircle className="size-8 text-red-500 mx-auto" />
              <h3 className="font-semibold text-black text-sm">Asset Not Found</h3>
              <p className="text-xs text-[#6a6a6a] max-w-sm mx-auto">{lookupError}</p>
            </GlassCard>
          ) : identifiedAsset ? (
            <GlassCard variant="light" className="p-7 space-y-6">
              {/* Asset Header */}
              <div className="flex items-start justify-between gap-3 pb-4 border-b border-black/10">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="size-2 rounded-full bg-[#ff5a24] animate-pulse" />
                    <span className="text-xs font-semibold uppercase tracking-wider text-[#7a7a7a]">
                      ASSET RECOGNIZED
                    </span>
                  </div>
                  <h2
                    className="text-3xl font-medium tracking-tight text-black mt-1"
                    style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
                  >
                    {identifiedAsset.id}
                  </h2>
                  <p className="text-xs text-[#666] mt-0.5">
                    {identifiedAsset.type} • {identifiedAsset.dealer}
                  </p>
                </div>
                <StatusBadge status={identifiedAsset.status} size="md" />
              </div>

              {/* Deployment Data Grid */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="p-3.5 rounded-xl border border-black/5 bg-black/[0.02]">
                  <span className="text-[10px] text-[#7a7a7a] uppercase font-semibold flex items-center gap-1">
                    <MapPin className="size-3 text-[#ff5a24]" />
                    <span>Current Site</span>
                  </span>
                  <span className="font-semibold text-black text-sm block mt-1">
                    {identifiedAsset.site?.name || "Yard Staging"}
                  </span>
                  <span className="text-[10px] text-[#777] block">
                    {identifiedAsset.site?.location || "Central Storage Logistics"}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl border border-black/5 bg-black/[0.02]">
                  <span className="text-[10px] text-[#7a7a7a] uppercase font-semibold flex items-center gap-1">
                    <User className="size-3 text-[#ff5a24]" />
                    <span>Assigned Operator</span>
                  </span>
                  <span className="font-semibold text-black text-sm block mt-1">
                    {identifiedAsset.operator?.name || (
                      <span className="text-[#ff5a24]">Unassigned</span>
                    )}
                  </span>
                  <span className="text-[10px] text-[#777] block">
                    {identifiedAsset.operator?.contact || "No operator assigned"}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl border border-black/5 bg-black/[0.02]">
                  <span className="text-[10px] text-[#7a7a7a] uppercase font-semibold flex items-center gap-1">
                    <DollarSign className="size-3 text-emerald-600" />
                    <span>Contract Day Rate</span>
                  </span>
                  <span className="font-mono font-bold text-black text-sm block mt-1">
                    {formatDayRate(identifiedAsset.daily_rate)}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl border border-black/5 bg-black/[0.02]">
                  <span className="text-[10px] text-[#7a7a7a] uppercase font-semibold">
                    Telemetry Engine Hours
                  </span>
                  <span className="font-mono font-bold text-black text-sm block mt-1">
                    {identifiedAsset.latest_telemetry?.engine_hours || 0}h
                  </span>
                </div>
              </div>

              {/* Action Trigger Card */}
              <div className="p-5 rounded-2xl border border-black/10 bg-white/80 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-black">Recommended Operational Action</span>
                  <span className="font-mono text-[10px] text-[#ff5a24] font-bold uppercase">
                    {hasActiveRental ? "Rental Active" : "Available in Yard"}
                  </span>
                </div>

                {hasActiveRental ? (
                  <div>
                    <p className="text-xs text-[#555] mb-3">
                      This unit is currently on-rent at <strong>{identifiedAsset.site?.name}</strong>. Initiate return check-in upon yard drop-off.
                    </p>
                    <button
                      onClick={() => setCheckinModalOpen(true)}
                      className="w-full py-3 rounded-xl bg-emerald-700 text-white font-semibold text-xs hover:bg-emerald-800 transition-all shadow-sm flex items-center justify-center gap-2"
                    >
                      <ShieldCheck className="size-4" />
                      <span>Initiate Equipment Check In</span>
                    </button>
                  </div>
                ) : (
                  <div>
                    <p className="text-xs text-[#555] mb-3">
                      This equipment is currently unassigned in yard storage. Dispatch to a certified construction site and operator.
                    </p>
                    <button
                      onClick={() => setCheckoutModalOpen(true)}
                      className="w-full py-3 rounded-xl bg-[#111111] text-white font-semibold text-xs hover:bg-black transition-all shadow-sm flex items-center justify-center gap-2"
                    >
                      <ArrowRight className="size-4 text-[#ff5a24]" />
                      <span>Initiate Equipment Check Out</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Asset Detail Link */}
              <div className="pt-2 text-center">
                <Link
                  href={`/assets/${identifiedAsset.id}`}
                  className="text-xs font-semibold text-[#ff5a24] hover:underline"
                >
                  View Full Asset Telemetry Detail Page →
                </Link>
              </div>
            </GlassCard>
          ) : (
            <GlassCard className="p-12 text-center space-y-3">
              <div className="size-14 rounded-2xl bg-black/5 grid place-items-center mx-auto text-[#7a7a7a]">
                <Truck className="size-6 text-[#ff5a24]" />
              </div>
              <h3 className="font-semibold text-black text-sm">No Asset Selected</h3>
              <p className="text-xs text-[#6a6a6a] max-w-xs mx-auto">
                Scan an equipment QR code or enter an ID (e.g. <strong>EQX1007</strong>) to inspect rental state.
              </p>
            </GlassCard>
          )}
        </div>
      </div>

      {/* Checkout Modal */}
      {identifiedAsset && (
        <CheckoutModal
          isOpen={checkoutModalOpen}
          onClose={() => setCheckoutModalOpen(false)}
          equipmentId={identifiedAsset.id}
          equipmentType={identifiedAsset.type}
          dailyRate={identifiedAsset.daily_rate}
          dealer={identifiedAsset.dealer}
          onSuccess={() => {
            lookupEquipment(identifiedAsset.id);
          }}
        />
      )}

      {/* Checkin Modal */}
      {identifiedAsset && (
        <CheckinModal
          isOpen={checkinModalOpen}
          onClose={() => setCheckinModalOpen(false)}
          equipmentId={identifiedAsset.id}
          equipmentType={identifiedAsset.type}
          currentSiteName={identifiedAsset.site?.name}
          currentOperatorName={identifiedAsset.operator?.name}
          currentStatus={identifiedAsset.status}
          onSuccess={() => {
            lookupEquipment(identifiedAsset.id);
          }}
        />
      )}
    </AppShell>
  );
}
