from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.site import SiteResponse
from app.schemas.operator import OperatorResponse
from app.schemas.rental import RentalResponse
from app.schemas.telemetry import TelemetryResponse
from app.schemas.alert import AlertResponse
from app.schemas.audit import AuditEventResponse


class EquipmentBase(BaseModel):
    id: str
    type: str
    dealer: str
    daily_rate: float
    metadata_json: Optional[Dict[str, Any]] = None


class EquipmentListItem(EquipmentBase):
    status: str
    current_rental: Optional[RentalResponse] = None
    site: Optional[SiteResponse] = None
    operator: Optional[OperatorResponse] = None
    latest_telemetry: Optional[TelemetryResponse] = None
    utilization_rate: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentDetailResponse(EquipmentBase):
    status: str
    current_rental: Optional[RentalResponse] = None
    site: Optional[SiteResponse] = None
    operator: Optional[OperatorResponse] = None
    latest_telemetry: Optional[TelemetryResponse] = None
    recent_telemetry: List[TelemetryResponse] = []
    rental_history: List[RentalResponse] = []
    active_alerts: List[AlertResponse] = []
    audit_timeline: List[AuditEventResponse] = []
    utilization_rate: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
