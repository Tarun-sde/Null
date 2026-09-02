import {
  DashboardKPIs,
  EquipmentListItem,
  EquipmentDetail,
  CheckoutPayload,
  CheckoutResponse,
  CheckinPayload,
  CheckinResponse,
  Site,
  Operator,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function fetchDashboardKPIs(): Promise<DashboardKPIs> {
  const res = await fetch(`${API_BASE_URL}/api/v1/dashboard`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch dashboard KPIs: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEquipmentList(params?: {
  search?: string;
  status?: string;
  site_id?: string;
  type?: string;
}): Promise<EquipmentListItem[]> {
  const query = new URLSearchParams();
  if (params?.search) query.append("search", params.search);
  if (params?.status) query.append("status", params.status);
  if (params?.site_id) query.append("site_id", params.site_id);
  if (params?.type) query.append("type", params.type);

  const url = `${API_BASE_URL}/api/v1/equipment${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch equipment list: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEquipmentDetail(id: string): Promise<EquipmentDetail> {
  const res = await fetch(`${API_BASE_URL}/api/v1/equipment/${encodeURIComponent(id)}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("NOT_FOUND");
    }
    throw new Error(`Failed to fetch equipment detail: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchSites(): Promise<Site[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/sites`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch sites: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchOperators(): Promise<Operator[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/operators`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch operators: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function checkoutEquipment(payload: CheckoutPayload): Promise<CheckoutResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rentals/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Checkout failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function checkinEquipment(payload: CheckinPayload): Promise<CheckinResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rentals/checkin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Check-in failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchAlerts(params?: {
  severity?: string;
  status?: string;
  equipment_id?: string;
  type?: string;
}): Promise<import("@/types").Alert[]> {
  const query = new URLSearchParams();
  if (params?.severity) query.append("severity", params.severity);
  if (params?.status) query.append("status", params.status);
  if (params?.equipment_id) query.append("equipment_id", params.equipment_id);
  if (params?.type) query.append("type", params.type);

  const url = `${API_BASE_URL}/api/v1/alerts${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch alerts: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchAnomalies(params?: {
  equipment_id?: string;
  severity?: string;
  type?: string;
}): Promise<import("@/types").Anomaly[]> {
  const query = new URLSearchParams();
  if (params?.equipment_id) query.append("equipment_id", params.equipment_id);
  if (params?.severity) query.append("severity", params.severity);
  if (params?.type) query.append("type", params.type);

  const url = `${API_BASE_URL}/api/v1/anomalies${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch anomalies: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEquipmentAnomalies(id: string): Promise<import("@/types").Anomaly[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/equipment/${encodeURIComponent(id)}/anomalies`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch equipment anomalies: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchForecasts(params?: {
  site_id?: string;
  equipment_type?: string;
  horizon_weeks?: number;
}): Promise<import("@/types").Forecast[]> {
  const query = new URLSearchParams();
  if (params?.site_id) query.append("site_id", params.site_id);
  if (params?.equipment_type) query.append("equipment_type", params.equipment_type);
  if (params?.horizon_weeks) query.append("horizon_weeks", params.horizon_weeks.toString());

  const url = `${API_BASE_URL}/api/v1/forecasts${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch forecasts: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchForecastSummary(params?: {
  site_id?: string;
  horizon_weeks?: number;
}): Promise<import("@/types").ForecastSummary> {
  const query = new URLSearchParams();
  if (params?.site_id) query.append("site_id", params.site_id);
  if (params?.horizon_weeks) query.append("horizon_weeks", params.horizon_weeks.toString());

  const url = `${API_BASE_URL}/api/v1/forecasts/summary${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch forecast summary: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// ==========================================
// Recommendations, Actions & Impact
// ==========================================

export async function fetchRecommendations(params?: {
  equipment_id?: string;
  priority?: string;
  status?: string;
  recommendation_type?: string;
}): Promise<import("@/types").Recommendation[]> {
  const query = new URLSearchParams();
  if (params?.equipment_id) query.append("equipment_id", params.equipment_id);
  if (params?.priority) query.append("priority", params.priority);
  if (params?.status) query.append("status", params.status);
  if (params?.recommendation_type) query.append("recommendation_type", params.recommendation_type);

  const url = `${API_BASE_URL}/api/v1/recommendations${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch recommendations: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEquipmentRecommendations(id: string): Promise<import("@/types").Recommendation[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/recommendations/equipment/${encodeURIComponent(id)}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch equipment recommendations: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function triggerActionFromRecommendation(
  recId: number,
  data?: {
    action_type?: string;
    notes?: string;
    actor?: string;
    payload?: Record<string, unknown>;
  }
): Promise<import("@/types").Action> {
  const res = await fetch(`${API_BASE_URL}/api/v1/recommendations/${recId}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data || {}),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to trigger action: ${res.status}`);
  }
  return res.json();
}

export async function fetchActions(params?: {
  status?: string;
  equipment_id?: string;
  action_type?: string;
  priority?: string;
}): Promise<import("@/types").Action[]> {
  const query = new URLSearchParams();
  if (params?.status) query.append("status", params.status);
  if (params?.equipment_id) query.append("equipment_id", params.equipment_id);
  if (params?.action_type) query.append("action_type", params.action_type);
  if (params?.priority) query.append("priority", params.priority);

  const url = `${API_BASE_URL}/api/v1/actions${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch actions: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchActionDetail(id: number): Promise<import("@/types").Action> {
  const res = await fetch(`${API_BASE_URL}/api/v1/actions/${id}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch action detail: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function createAction(data: {
  equipment_id: string;
  action_type: string;
  recommendation_id?: number;
  alert_id?: number;
  priority?: string;
  notes?: string;
  actor?: string;
  payload?: Record<string, unknown>;
}): Promise<import("@/types").Action> {
  const res = await fetch(`${API_BASE_URL}/api/v1/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create action: ${res.status}`);
  }
  return res.json();
}

export async function completeAction(
  id: number,
  data?: {
    notes?: string;
    actor?: string;
    payload?: Record<string, unknown>;
  }
): Promise<import("@/types").Action> {
  const res = await fetch(`${API_BASE_URL}/api/v1/actions/${id}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data || {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to complete action: ${res.status}`);
  }
  return res.json();
}

export async function cancelAction(
  id: number,
  data?: {
    reason?: string;
    actor?: string;
  }
): Promise<import("@/types").Action> {
  const res = await fetch(`${API_BASE_URL}/api/v1/actions/${id}/cancel`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data || {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to cancel action: ${res.status}`);
  }
  return res.json();
}

export async function resolveAlert(
  id: number,
  data?: {
    resolution_notes?: string;
    actor?: string;
  }
): Promise<import("@/types").Alert> {
  const res = await fetch(`${API_BASE_URL}/api/v1/alerts/${id}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data || {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to resolve alert: ${res.status}`);
  }
  return res.json();
}

export async function fetchImpactSummary(params?: { site_id?: string }): Promise<import("@/types").ImpactSummary> {
  const query = new URLSearchParams();
  if (params?.site_id) query.append("site_id", params.site_id);

  const url = `${API_BASE_URL}/api/v1/impact${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch impact summary: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchActionImpactDetail(actionId: number): Promise<import("@/types").ImpactDetail> {
  const res = await fetch(`${API_BASE_URL}/api/v1/actions/${actionId}/impact`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch action impact detail: ${res.status} ${res.statusText}`);
  }
  return res.json();
}
export async function createEquipment(payload: {
  id: string;
  type: string;
  dealer: string;
  daily_rate: number;
  model?: string;
  serial?: string;
}): Promise<import("@/types").EquipmentDetail> {
  const res = await fetch(`${API_BASE_URL}/api/v1/equipment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || `Failed to create equipment: ${res.status}`);
  }
  return res.json();
}

export interface ChatMessageHistoryItem {
  role: "user" | "assistant" | "model";
  content: string;
}

export interface ChatResponse {
  reply: string;
  is_configured: boolean;
  grounded: boolean;
  model?: string;
  timestamp: string;
}

export async function sendChatMessage(
  message: string,
  history?: ChatMessageHistoryItem[]
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || `Chat request failed: ${res.status}`);
  }
  return res.json();
}

export async function streamChatMessage(
  message: string,
  history: ChatMessageHistoryItem[] | undefined,
  callbacks: {
    onChunk: (text: string) => void;
    onStage?: (stageText: string) => void;
    onDone: (meta: { is_configured: boolean; grounded: boolean; model?: string }) => void;
    onError: (errMessage: string) => void;
  }
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      callbacks.onError(err.detail || err.message || `Streaming request failed: ${res.status}`);
      return;
    }

    if (!res.body) {
      callbacks.onError("No streaming response body received.");
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          try {
            const data = JSON.parse(trimmed.slice(6));
            if (data.type === "stage" && callbacks.onStage) {
              callbacks.onStage(data.text);
            } else if (data.type === "chunk") {
              callbacks.onChunk(data.text);
            } else if (data.type === "done") {
              callbacks.onDone({
                is_configured: data.is_configured ?? true,
                grounded: data.grounded ?? true,
                model: data.model,
              });
            } else if (data.type === "error") {
              callbacks.onError(data.reply || "Gemini service encountered an issue.");
            }
          } catch {
            // Ignore unparsed stream chunks
          }
        }
      }
    }
  } catch (err: unknown) {
    const errMsg = err instanceof Error ? err.message : "Failed to connect to streaming chat.";
    callbacks.onError(errMsg);
  }
}

export async function fetchChatStatus(): Promise<{ is_configured: boolean; model: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/chat/status`, { cache: "no-store" });
  if (!res.ok) {
    return { is_configured: false, model: "gemini-3.6-flash" };
  }
  return res.json();
}
