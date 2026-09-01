"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { TelemetryStreamEvent, EquipmentListItem, DashboardKPIs } from "@/types";
import { fetchEquipmentList, fetchDashboardKPIs } from "./api";

export type ConnectionState = "LIVE" | "RECONNECTING" | "POLLING" | "OFFLINE";

interface UseTelemetryStreamOptions {
  onTelemetry?: (event: TelemetryStreamEvent) => void;
  onFullRefresh?: (data: { equipment: EquipmentListItem[]; kpis: DashboardKPIs }) => void;
  enabled?: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const POLLING_INTERVAL_MS = 6000;

export function useTelemetryStream({
  onTelemetry,
  onFullRefresh,
  enabled = true,
}: UseTelemetryStreamOptions = {}) {
  const [connectionState, setConnectionState] = useState<ConnectionState>("OFFLINE");
  const [lastEventTime, setLastEventTime] = useState<Date | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const pollingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingActiveRef = useRef(false);

  // Stable callbacks via ref
  const onTelemetryRef = useRef(onTelemetry);
  onTelemetryRef.current = onTelemetry;

  const onFullRefreshRef = useRef(onFullRefresh);
  onFullRefreshRef.current = onFullRefresh;

  // Execute fallback poll
  const executePoll = useCallback(async () => {
    try {
      const [equipment, kpis] = await Promise.all([
        fetchEquipmentList(),
        fetchDashboardKPIs(),
      ]);
      setLastEventTime(new Date());
      if (onFullRefreshRef.current) {
        onFullRefreshRef.current({ equipment, kpis });
      }
    } catch (err) {
      console.warn("[Polling Fallback] Error fetching data:", err);
    }
  }, []);

  // Start polling fallback loop
  const startPolling = useCallback(() => {
    if (isPollingActiveRef.current) return;
    isPollingActiveRef.current = true;
    setConnectionState("POLLING");
    console.info("[TelemetryStream] SSE unavailable. Starting 6-second polling fallback.");

    // Initial poll
    executePoll();

    if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    pollingTimerRef.current = setInterval(executePoll, POLLING_INTERVAL_MS);
  }, [executePoll]);

  // Stop polling fallback loop
  const stopPolling = useCallback(() => {
    if (!isPollingActiveRef.current) return;
    isPollingActiveRef.current = false;
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }
    console.info("[TelemetryStream] SSE restored. Terminating fallback polling.");
  }, []);

  // Connect to SSE stream
  const connectSSE = useCallback(() => {
    if (!enabled) return;

    // Clean up previous instance
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    const streamUrl = `${API_BASE_URL}/api/v1/telemetry/stream`;
    console.info(`[TelemetryStream] Connecting to SSE stream: ${streamUrl}`);
    setConnectionState("RECONNECTING");

    try {
      const es = new EventSource(streamUrl);
      eventSourceRef.current = es;

      es.onopen = () => {
        console.info("[TelemetryStream] SSE Connection Established (LIVE)");
        setConnectionState("LIVE");
        stopPolling();
      };

      es.addEventListener("telemetry", (e: MessageEvent) => {
        try {
          const payload = JSON.parse(e.data) as TelemetryStreamEvent;
          setLastEventTime(new Date());
          if (onTelemetryRef.current) {
            onTelemetryRef.current(payload);
          }
        } catch (parseErr) {
          console.warn("[TelemetryStream] Failed to parse telemetry event:", parseErr);
        }
      });

      es.onerror = (err) => {
        console.warn("[TelemetryStream] SSE Connection Error / Closed:", err);
        es.close();
        eventSourceRef.current = null;

        // Transition to fallback polling
        startPolling();

        // Schedule SSE reconnect attempt after 5 seconds
        if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          if (enabled) {
            console.info("[TelemetryStream] Attempting SSE reconnection...");
            connectSSE();
          }
        }, 5000);
      };
    } catch (e) {
      console.error("[TelemetryStream] Failed to initialize EventSource:", e);
      startPolling();
    }
  }, [enabled, startPolling, stopPolling]);

  useEffect(() => {
    if (!enabled) {
      setConnectionState("OFFLINE");
      return;
    }

    connectSSE();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      isPollingActiveRef.current = false;
    };
  }, [enabled, connectSSE]);

  return {
    connectionState,
    lastEventTime,
    reconnect: connectSSE,
  };
}
