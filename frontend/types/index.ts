export type EquipmentStatus = "ACTIVE" | "IDLE" | "DUE_SOON" | "OVERDUE" | "UNASSIGNED";

export interface Site {
  id: string;
  name: string;
  location?: string | null;
  latitude: number;
  longitude: number;
  created_at: string;
}

export interface Operator {
  id: string;
  name: string;
  contact?: string | null;
  created_at: string;
}

export interface Telemetry {
  id?: number;
  equipment_id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  engine_hours: number;
  idle_hours: number;
  fuel_pct: number;
  created_at?: string;
}

export interface TelemetryStreamEvent {
  equipment_id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  engine_hours: number;
  idle_hours: number;
  fuel_pct: number;
  utilization_rate: number;
  status: string;
}

export interface Rental {
  id: number;
  equipment_id: string;
  site_id?: string | null;
  operator_id?: string | null;
  checked_out_at?: string | null;
  due_at?: string | null;
  checked_in_at?: string | null;
  daily_rate: number;
  condition_notes?: string | null;
  created_at: string;
  updated_at: string;
  site?: Site | null;
  operator?: Operator | null;
}

export interface Alert {
  id: number;
  equipment_id: string;
  alert_type: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  message: string;
  status: "OPEN" | "RESOLVED" | "ACKNOWLEDGED" | string;
  metadata_json?: Record<string, any> | null;
  action_label?: string | null;
  created_at: string;
  resolved_at?: string | null;
}


export interface AuditEvent {
  id: number;
  event_type: string;
  equipment_id?: string | null;
  actor?: string | null;
  timestamp: string;
  metadata_json?: Record<string, any> | null;
  created_at: string;
}

export interface EquipmentListItem {
  id: string;
  type: string;
  dealer: string;
  daily_rate: number;
  status: EquipmentStatus | string;
  current_rental?: Rental | null;
  site?: Site | null;
  operator?: Operator | null;
  latest_telemetry?: Telemetry | null;
  utilization_rate: number;
  metadata_json?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface EquipmentDetail extends EquipmentListItem {
  recent_telemetry: Telemetry[];
  rental_history: Rental[];
  active_alerts: Alert[];
  audit_timeline: AuditEvent[];
}

export interface DashboardKPIs {
  total_equipment: number;
  active: number;
  idle: number;
  due_soon: number;
  overdue: number;
  unassigned: number;
  status_counts: Record<string, number>;
  open_alerts: number;
  fleet_utilization_pct: number;
}

export interface CheckoutPayload {
  equipment_id: string;
  site_id: string;
  operator_id: string;
  due_at: string;
  daily_rate?: number;
  condition_notes?: string;
  actor?: string;
}

export interface CheckoutResponse {
  success: boolean;
  equipment_id: string;
  status: string;
  rental: Rental;
  audit_event: AuditEvent;
}

export interface CheckinPayload {
  equipment_id: string;
  condition?: string;
  notes?: string;
  actor?: string;
}

export interface CheckinResponse {
  success: boolean;
  equipment_id: string;
  status: string;
  rental: Rental;
  audit_event: AuditEvent;
}

export interface Anomaly {
  equipment_id: string;
  anomaly_type: string;
  anomaly_score: number;
  severity: "CRITICAL" | "WARNING" | "INFO" | string;
  explanation: string;
  supporting_signals: Record<string, any>;
  recommended_action_category?: string | null;
  detected_at: string;
}

export interface Forecast {
  id: number;
  site_id?: string | null;
  site_name?: string | null;
  equipment_type: string;
  forecast_date: string;
  predicted_units: number;
  confidence: number;
  backtest_error?: number | null;
  drivers?: Record<string, any> | null;
  explanation?: string | null;
  created_at: string;
}

export interface ForecastSummary {
  total_forecasted_units: number;
  avg_confidence: number;
  avg_backtest_error?: number | null;
  horizon_weeks: number;
  forecasts: Forecast[];
}

