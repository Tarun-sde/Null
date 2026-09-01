"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Calendar,
  Clock,
  DollarSign,
  Fuel,
  Gauge,
  MapPin,
  QrCode,
  ShieldAlert,
  Sparkles,
  Truck,
  User,
  History,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { GlassCard } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { TelemetryChart } from "@/components/assets/TelemetryChart";
import { MiniMap } from "@/components/assets/MiniMap";
import { CardSkeleton } from "@/components/ui/SkeletonLoader";
import { EmptyState } from "@/components/ui/EmptyState";
import { fetchEquipmentDetail } from "@/lib/api";
import { EquipmentDetail, EquipmentStatus } from "@/types";
import { STATUS_CONFIG } from "@/lib/constants";
import { cn } from "@/lib/utils";

export default function AssetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [equipment, setEquipment] = useState<EquipmentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const loadDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchEquipmentDetail(id);
        setEquipment(data);
      } catch (err: any) {
        console.error("Error loading asset detail:", err);
        setError(err.message === "NOT_FOUND" ? "Equipment Not Found" : "Failed to load asset");
      } finally {
        setLoading(false);
      }
    };
    loadDetail();
  }, [id]);

  if (loading) {
    return (
      <AppShell>
        <div className="space-y-8 animate-pulse">
          <div className="h-8 w-48 bg-black/10 rounded-lg" />
          <div className="grid lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
          <div className="h-96 bg-black/10 rounded-2xl" />
        </div>
      </AppShell>
    );
  }

  if (error || !equipment) {
    return (
      <AppShell>
        <EmptyState
          title="Equipment Asset Not Found"
          description={`No record found for asset identifier "${id}". Please check the fleet registry.`}
          actionText="Back to Fleet Assets"
          onAction={() => router.push("/assets")}
        />
      </AppShell>
    );
  }

  const model = (equipment.metadata_json as any)?.model || "Standard Heavy Spec";
  const serial = (equipment.metadata_json as any)?.serial || "SN-PENDING";
  const utilPct = Math.round(equipment.utilization_rate * 100);
  const engineHours = equipment.latest_telemetry?.engine_hours || 0;
  const idleHours = equipment.latest_telemetry?.idle_hours || 0;
  const fuelPct = equipment.latest_telemetry?.fuel_pct ?? 100;
  const activeHours = Math.max(0, engineHours - idleHours);

  return (
    <AppShell>
      {/* Breadcrumb & Navigation */}
      <div className="mb-6 flex items-center justify-between">
        <Link
          href="/assets"
          className="inline-flex items-center gap-2 text-xs font-semibold text-[#6a6a6a] hover:text-black transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          <span>Back to Fleet Ledger</span>
        </Link>
        <span className="text-xs font-mono text-[#7a7a7a]">
          Node ID: <strong className="text-black">{equipment.id}</strong>
        </span>
      </div>

      {/* Main Asset Header */}
      <section className="mb-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-black/10">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h1
              className="text-4xl sm:text-5xl font-medium tracking-tight text-black"
              style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
            >
              {equipment.id}
            </h1>
            <StatusBadge status={equipment.status} size="lg" />
          </div>

          <p className="mt-2 text-base text-[#4c4c4c] flex flex-wrap items-center gap-2">
            <span className="font-semibold text-black">{equipment.type}</span>
            <span>•</span>
            <span>{model}</span>
            <span>•</span>
            <span>{equipment.dealer}</span>
            <span>•</span>
            <span className="font-mono text-xs text-[#7a7a7a]">Serial: {serial}</span>
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <button className="flex items-center gap-2 rounded-xl border border-black/15 bg-white/70 px-4 py-2.5 text-xs font-medium text-black shadow-sm hover:bg-white transition-all">
            <QrCode className="size-4 text-[#ff5a24]" />
            <span>Generate Handoff QR</span>
          </button>
          <button className="flex items-center gap-2 rounded-xl bg-[#111111] px-5 py-2.5 text-xs font-medium text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:bg-black transition-all">
            <span>Reassign / Return</span>
          </button>
        </div>
      </section>

      {/* 4 Metric KPI Cards */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <GlassCard className="p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#6a6a6a]">Engine Runtime</span>
            <Gauge className="size-4 text-[#ff5a24]" />
          </div>
          <p
            className="text-3xl sm:text-4xl font-medium text-black mt-3 leading-none"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            {engineHours}h
          </p>
          <span className="text-[11px] text-[#7a7a7a] mt-2">
            Active: <strong className="text-black">{activeHours}h</strong> • Idle: <strong className="text-black">{idleHours}h</strong>
          </span>
        </GlassCard>

        <GlassCard className="p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#6a6a6a]">Utilization Rate</span>
            <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>
          <p
            className="text-3xl sm:text-4xl font-medium text-black mt-3 leading-none"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            {utilPct}%
          </p>
          <div className="w-full bg-black/10 h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className={cn("h-full rounded-full", utilPct < 20 ? "bg-amber-500" : "bg-[#ff5a24]")}
              style={{ width: `${Math.min(100, Math.max(5, utilPct))}%` }}
            />
          </div>
        </GlassCard>

        <GlassCard className="p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#6a6a6a]">Fuel Reservoir</span>
            <Fuel className="size-4 text-[#ff5a24]" />
          </div>
          <p
            className="text-3xl sm:text-4xl font-medium text-black mt-3 leading-none font-mono"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            {fuelPct}%
          </p>
          <span className="text-[11px] text-[#7a7a7a] mt-2">
            Estimated ~{Math.round(fuelPct * 1.8)} gallons remaining
          </span>
        </GlassCard>

        <GlassCard className="p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#6a6a6a]">Contract Day Rate</span>
            <DollarSign className="size-4 text-emerald-600" />
          </div>
          <p
            className="text-3xl sm:text-4xl font-medium text-black mt-3 leading-none font-mono"
            style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
          >
            ${equipment.daily_rate}
          </p>
          <span className="text-[11px] text-[#7a7a7a] mt-2">
            Supplier: <strong className="text-black">{equipment.dealer}</strong>
          </span>
        </GlassCard>
      </section>

      {/* Center Layout: Telemetry Charts (2 cols) + Assignment & MiniMap (1 col) */}
      <section className="grid lg:grid-cols-3 gap-8 mb-8 items-stretch">
        <div className="lg:col-span-2">
          <TelemetryChart telemetry={equipment.recent_telemetry} />
        </div>
        <div className="space-y-6 flex flex-col justify-between">
          {/* Active Assignment Card */}
          <GlassCard className="p-6 flex-1 flex flex-col justify-between">
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
                Current Deployment
              </h3>
              <p className="text-xs text-[#7a7a7a] mt-0.5">Active site &amp; operator assignment</p>
            </div>

            <div className="my-4 space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-black/[0.03] border border-black/5">
                <span className="text-[10px] uppercase font-bold text-[#7a7a7a] block">Assigned Site</span>
                <span className="font-semibold text-black text-sm mt-0.5 block">
                  {equipment.site?.name || "Yard Staging Depot"}
                </span>
                <span className="text-[11px] text-[#666] block mt-0.5">
                  {equipment.site?.location || "Central Storage Logistics"}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-black/[0.03] border border-black/5">
                <span className="text-[10px] uppercase font-bold text-[#7a7a7a] block">Certified Operator</span>
                <span className="font-semibold text-black text-sm mt-0.5 block">
                  {equipment.operator?.name || (
                    <span className="text-[#ff5a24]">Missing Assignment</span>
                  )}
                </span>
                <span className="text-[11px] text-[#666] block mt-0.5">
                  {equipment.operator?.contact || "No operator contact linked"}
                </span>
              </div>
            </div>

            <div className="text-[11px] text-[#7a7a7a] flex items-center justify-between border-t border-black/10 pt-3">
              <span>Checkout: {equipment.current_rental?.checked_out_at ? new Date(equipment.current_rental.checked_out_at).toLocaleDateString() : "N/A"}</span>
              <span>Due: {equipment.current_rental?.due_at ? new Date(equipment.current_rental.due_at).toLocaleDateString() : "N/A"}</span>
            </div>
          </GlassCard>

          {/* MiniMap */}
          <div className="h-60">
            <MiniMap
              site={equipment.site}
              latitude={equipment.latest_telemetry?.latitude}
              longitude={equipment.latest_telemetry?.longitude}
            />
          </div>
        </div>
      </section>

      {/* AI Operational Insight & Active Alerts */}
      <section className="grid md:grid-cols-2 gap-8 mb-8 items-stretch">
        {/* AI Insight Card */}
        <GlassCard variant="dark" className="p-7 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="size-4 text-[#ff5a24]" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-white">
                  Operational Recommendation
                </h3>
              </div>
              <span className="text-xs font-mono text-[#ff5a24] bg-white/10 px-2.5 py-0.5 rounded-full border border-white/20">
                AI Optimization
              </span>
            </div>

            <div className="mt-5 space-y-3">
              {equipment.status === "IDLE" && (
                <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4">
                  <p className="font-semibold text-white text-sm">
                    Reassign Asset: High Idle Accumulation
                  </p>
                  <p className="text-xs text-white/80 mt-1 leading-relaxed">
                    This unit has recorded {idleHours} hours of idle time with only {utilPct}% utilization. Reallocating to Highland Medical Center will reduce standby costs by ~${equipment.daily_rate * 3}.
                  </p>
                </div>
              )}

              {equipment.status === "OVERDUE" && (
                <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
                  <p className="font-semibold text-white text-sm">
                    Action Required: Off-Rent Immediate Handoff
                  </p>
                  <p className="text-xs text-white/80 mt-1 leading-relaxed">
                    Contract has exceeded its scheduled return date. Surcharge penalties are accumulating at ${equipment.daily_rate}/day.
                  </p>
                </div>
              )}

              {equipment.status === "UNASSIGNED" && (
                <div className="rounded-xl border border-[#ff5a24]/30 bg-[#ff5a24]/10 p-4">
                  <p className="font-semibold text-white text-sm">
                    Assign Operator or Return to Depot
                  </p>
                  <p className="text-xs text-white/80 mt-1 leading-relaxed">
                    Asset is deployed on site but lacks certified operator binding. Assign an authorized driver to resume telemetry tracking.
                  </p>
                </div>
              )}

              {(equipment.status === "ACTIVE" || equipment.status === "DUE_SOON") && (
                <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
                  <p className="font-semibold text-white text-sm">
                    Operational Performance Optimal
                  </p>
                  <p className="text-xs text-white/80 mt-1 leading-relaxed">
                    Equipment is operating within target fuel efficiency and runtime thresholds. No immediate action required.
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-white/70">
            <span>Model Confidence: 94.8%</span>
            <button className="rounded-lg bg-[#ff5a24] px-4 py-2 text-xs font-semibold text-white hover:bg-[#ff6330] transition-colors">
              Execute Optimization Action
            </button>
          </div>
        </GlassCard>

        {/* Active Alerts for this asset */}
        <GlassCard variant="light" className="p-7 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldAlert className="size-4 text-[#ff5a24]" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
                  Asset Anomaly Logs
                </h3>
              </div>
              <span className="text-xs font-mono text-[#7a7a7a]">
                {equipment.active_alerts.length} Active
              </span>
            </div>

            <div className="mt-5 space-y-3">
              {equipment.active_alerts.length === 0 ? (
                <div className="py-8 text-center text-xs text-[#7a7a7a]">
                  <CheckCircle2 className="size-6 text-emerald-600 mx-auto mb-2" />
                  No open anomalies detected for {equipment.id}.
                </div>
              ) : (
                equipment.active_alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="p-4 rounded-xl border border-black/10 bg-white/70 shadow-xs space-y-1"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-black">{alert.alert_type}</span>
                      <span className="font-mono text-[10px] text-[#ff5a24] font-semibold uppercase">
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-xs text-[#555] leading-snug">{alert.message}</p>
                    <span className="text-[10px] text-[#888] font-mono block pt-1">
                      Reported: {new Date(alert.created_at).toLocaleString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-black/10 text-xs text-[#7a7a7a] flex items-center justify-between">
            <span>Automated Diagnostic Surveillance</span>
            <span className="text-emerald-700 font-semibold">Sensor Grid Synced</span>
          </div>
        </GlassCard>
      </section>

      {/* Rental History & Audit Timeline */}
      <section className="grid lg:grid-cols-2 gap-8 mb-12">
        {/* Rental Contracts History */}
        <GlassCard className="p-7">
          <div className="flex items-center justify-between pb-4 border-b border-black/10">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
              Rental Contract History
            </h3>
            <span className="text-xs font-mono text-[#7a7a7a]">
              {equipment.rental_history.length} Record(s)
            </span>
          </div>

          <div className="mt-4 space-y-3">
            {equipment.rental_history.map((rental) => (
              <div
                key={rental.id}
                className="p-3.5 rounded-xl border border-black/5 bg-white/50 text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between font-semibold text-black">
                  <span>Contract #{rental.id}</span>
                  <span className="font-mono">${rental.daily_rate}/day</span>
                </div>
                <div className="text-[#666] flex flex-wrap items-center gap-2 text-[11px]">
                  <span>Site: {rental.site?.name || "Yard"}</span>
                  <span>•</span>
                  <span>Operator: {rental.operator?.name || "Unassigned"}</span>
                </div>
                {rental.condition_notes && (
                  <p className="text-[11px] text-[#777] italic pt-1">
                    "{rental.condition_notes}"
                  </p>
                )}
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Audit Timeline */}
        <GlassCard className="p-7">
          <div className="flex items-center justify-between pb-4 border-b border-black/10">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-black">
              Lifecycle Audit Events
            </h3>
            <span className="text-xs font-mono text-[#7a7a7a]">
              {equipment.audit_timeline.length} Event(s)
            </span>
          </div>

          <div className="mt-4 space-y-3">
            {equipment.audit_timeline.length === 0 ? (
              <p className="py-6 text-center text-xs text-[#7a7a7a]">
                No recorded audit events for this equipment yet.
              </p>
            ) : (
              equipment.audit_timeline.map((evt) => (
                <div
                  key={evt.id}
                  className="p-3 rounded-xl border border-black/5 bg-white/50 text-xs flex items-start justify-between gap-3"
                >
                  <div>
                    <span className="font-semibold text-black block">{evt.event_type}</span>
                    <span className="text-[11px] text-[#666] block">
                      Actor: {evt.actor || "Automated Process"}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-[#888] shrink-0">
                    {new Date(evt.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
              ))
            )}
          </div>
        </GlassCard>
      </section>
    </AppShell>
  );
}
