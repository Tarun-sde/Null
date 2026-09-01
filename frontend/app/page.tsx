"use client";

import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { HeroOverview } from "@/components/dashboard/HeroOverview";
import { MetricCard } from "@/components/ui/MetricCard";
import { FleetStatusDonut } from "@/components/dashboard/FleetStatusDonut";
import { FleetMapCard } from "@/components/dashboard/FleetMapCard";
import { AlertsPanel } from "@/components/dashboard/AlertsPanel";
import { RecommendationsPanel } from "@/components/dashboard/RecommendationsPanel";
import { ActivityTimeline } from "@/components/dashboard/ActivityTimeline";
import { EquipmentTable } from "@/components/dashboard/EquipmentTable";
import { CardSkeleton, TableSkeleton } from "@/components/ui/SkeletonLoader";
import { EmptyState } from "@/components/ui/EmptyState";
import { fetchDashboardKPIs, fetchEquipmentList, fetchAlerts, fetchRecommendations } from "@/lib/api";
import { useTelemetryStream } from "@/lib/useTelemetryStream";
import { DashboardKPIs, EquipmentListItem, TelemetryStreamEvent, Telemetry, Alert, Recommendation } from "@/types";

export default function DashboardPage() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [equipmentList, setEquipmentList] = useState<EquipmentListItem[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initial load
  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [kpiRes, eqRes, alertRes, recRes] = await Promise.all([
        fetchDashboardKPIs(),
        fetchEquipmentList(),
        fetchAlerts({ status: "OPEN" }).catch(() => []),
        fetchRecommendations({ status: "PENDING" }).catch(() => []),
      ]);
      setKpis(kpiRes);
      setEquipmentList(eqRes);
      setAlerts(alertRes);
      setRecommendations(recRes);
    } catch (err: any) {
      console.error("Dashboard data load error:", err);
      setError(err.message || "Failed to load fleet data");
    } finally {
      setLoading(false);
    }
  };



  useEffect(() => {
    loadInitialData();
  }, []);

  // Handle incoming real-time telemetry events from SSE
  const handleLiveTelemetry = useCallback((event: TelemetryStreamEvent) => {
    setEquipmentList((prevList) => {
      let statusChanged = false;
      const updatedList = prevList.map((item) => {
        if (item.id === event.equipment_id) {
          if (item.status !== event.status) {
            statusChanged = true;
          }
          const updatedTelemetry: Telemetry = {
            equipment_id: event.equipment_id,
            timestamp: typeof event.timestamp === "string" ? event.timestamp : new Date(event.timestamp).toISOString(),
            latitude: event.latitude,
            longitude: event.longitude,
            engine_hours: event.engine_hours,
            idle_hours: event.idle_hours,
            fuel_pct: event.fuel_pct,
          };
          return {
            ...item,
            status: event.status,
            utilization_rate: event.utilization_rate,
            latest_telemetry: updatedTelemetry,
          };
        }
        return item;
      });

      // Recalculate KPIs locally if status changed
      if (statusChanged) {
        setKpis((prevKpis) => {
          if (!prevKpis) return prevKpis;
          const statusCounts: Record<string, number> = {};
          let active = 0;
          let idle = 0;
          let due_soon = 0;
          let overdue = 0;
          let unassigned = 0;

          updatedList.forEach((eq) => {
            const st = eq.status.toUpperCase();
            statusCounts[st] = (statusCounts[st] || 0) + 1;
            if (st === "ACTIVE") active++;
            else if (st === "IDLE") idle++;
            else if (st === "DUE_SOON") due_soon++;
            else if (st === "OVERDUE") overdue++;
            else if (st === "UNASSIGNED") unassigned++;
          });

          return {
            ...prevKpis,
            active,
            idle,
            due_soon,
            overdue,
            unassigned,
            status_counts: statusCounts,
          };
        });
      }

      return updatedList;
    });
  }, []);

  // Handle fallback polling updates
  const handleFullRefresh = useCallback((data: { equipment: EquipmentListItem[]; kpis: DashboardKPIs }) => {
    setEquipmentList(data.equipment);
    setKpis(data.kpis);
  }, []);

  // Realtime hook
  const { connectionState } = useTelemetryStream({
    onTelemetry: handleLiveTelemetry,
    onFullRefresh: handleFullRefresh,
    enabled: !loading && !error,
  });

  return (
    <AppShell
      openAlertsCount={kpis?.open_alerts ?? 4}
      connectionState={connectionState}
    >
      {/* Hero Overview */}
      <HeroOverview
        fleetUtilizationPct={kpis?.fleet_utilization_pct ?? 63.2}
        totalAssets={kpis?.total_equipment ?? equipmentList.length}
        activeAssets={kpis?.active ?? 2}
      />

      {/* KPI Cards Grid */}
      <section className="mb-10">
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-5">
            {[...Array(5)].map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-5">
            <MetricCard
              title="Active Fleet"
              value={kpis?.active ?? 2}
              subtext="Under active rental contract"
              trend="In Production"
              trendPositive={true}
              sparklineColor="#16a34a"
              statusDotColor="bg-emerald-500"
            />
            <MetricCard
              title="Idle Units"
              value={kpis?.idle ?? 1}
              subtext="High idle hours (>8h)"
              trend="Requires Action"
              trendPositive={false}
              sparklineColor="#eab308"
              statusDotColor="bg-amber-500"
            />
            <MetricCard
              title="Due Soon"
              value={kpis?.due_soon ?? 1}
              subtext="Expiring within 48 hours"
              trend="Expiring"
              trendPositive={false}
              sparklineColor="#ff5a24"
              statusDotColor="bg-[#ff5a24]"
            />
            <MetricCard
              title="Overdue"
              value={kpis?.overdue ?? 1}
              subtext="Surcharge accumulating"
              trend="Critical Surcharge"
              trendPositive={false}
              sparklineColor="#dc2626"
              statusDotColor="bg-red-600"
            />
            <MetricCard
              title="Unassigned"
              value={kpis?.unassigned ?? 2}
              subtext="Missing operator or yard"
              trend="Off-Rent"
              trendPositive={true}
              sparklineColor="#64748b"
              statusDotColor="bg-slate-400"
            />
          </div>
        )}
      </section>

      {/* Center Section: Donut + Tactical Map */}
      <section className="mb-10 grid lg:grid-cols-3 gap-8 items-stretch">
        <div className="lg:col-span-1">
          <FleetStatusDonut
            statusCounts={
              kpis?.status_counts || {
                ACTIVE: 2,
                IDLE: 1,
                DUE_SOON: 1,
                OVERDUE: 1,
                UNASSIGNED: 2,
              }
            }
            totalEquipment={kpis?.total_equipment || 7}
          />
        </div>
        <div className="lg:col-span-2">
          <FleetMapCard equipmentList={equipmentList} />
        </div>
      </section>

      {/* Triad Intelligence Section: Alerts + Recommendations + Timeline */}
      <section className="mb-10 grid md:grid-cols-2 lg:grid-cols-3 gap-8 items-stretch">
        <div>
          <AlertsPanel alerts={alerts} />
        </div>
        <div>
          <RecommendationsPanel
            recommendations={recommendations}
            onActionTriggered={loadInitialData}
          />
        </div>
        <div>
          <ActivityTimeline />
        </div>
      </section>

      {/* Fleet Ledger Table */}
      <section className="mb-12">
        {loading ? (
          <TableSkeleton />
        ) : error ? (
          <EmptyState
            title="Unable to Load Equipment Ledger"
            description="The connection to the RentSense backend API failed. Ensure the server is running on http://localhost:8000."
            actionText="Retry Connection"
            onAction={loadInitialData}
          />
        ) : (
          <EquipmentTable equipmentList={equipmentList} />
        )}
      </section>
    </AppShell>
  );
}
