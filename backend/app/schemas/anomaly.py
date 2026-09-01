from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AnomalyResponse(BaseModel):
    equipment_id: str
    anomaly_type: str = Field(..., description="IDLE, ZERO_RUNTIME, MISSING_ASSIGNMENT, OVERDUE, LOW_UTILIZATION")
    anomaly_score: int = Field(..., ge=0, le=100, description="Deterministic anomaly score between 0 and 100")
    severity: str = Field(..., description="INFO, WARNING, or CRITICAL")
    explanation: str = Field(..., description="Plain-language explanation with exact metrics")
    supporting_signals: Dict[str, Any] = Field(default_factory=dict, description="Observed parameter values and thresholds")
    recommended_action_category: Optional[str] = Field(None, description="Category of suggested triage action")
    detected_at: datetime = Field(..., description="Timestamp when the anomaly was evaluated")


class FleetAnomalySummary(BaseModel):
    total_anomalies: int
    critical_count: int
    warning_count: int
    info_count: int
    anomalies_by_type: Dict[str, int]
    anomalies: List[AnomalyResponse]
