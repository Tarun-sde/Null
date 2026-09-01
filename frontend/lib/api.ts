import { DashboardKPIs, EquipmentListItem, EquipmentDetail } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
