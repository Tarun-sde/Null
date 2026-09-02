from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class ImpactRecordBase(BaseModel):
    action_id: Optional[int] = None
    equipment_id: str
    site_id: Optional[str] = None
    impact_type: str = Field(..., description="IDLE_AVOIDANCE, EARLY_RETURN, OVERDUE_SURCHARGE_AVOIDED, UTILIZATION_RECOVERY")
    estimated_amount: float
    realized_amount: float = 0.0
    currency: str = "INR"
    calculation_basis: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None


class ImpactResponse(ImpactRecordBase):
    id: int
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImpactDetailResponse(BaseModel):
    action_id: Optional[int] = None
    equipment_id: str
    action_type: str
    impact_type: str
    daily_rate: float
    baseline_metrics: Dict[str, Any]
    avoided_cost: float
    realized_savings: float
    calculation_basis: str
    status: str
    calculated_at: datetime


class ImpactSummaryResponse(BaseModel):
    total_estimated_impact: float
    total_realized_savings: float
    completed_actions_count: int
    savings_by_action_type: Dict[str, float]
    savings_by_site: Dict[str, float]
    savings_by_equipment_type: Dict[str, float]
    recent_impact_records: List[ImpactResponse]
