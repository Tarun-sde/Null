from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.site import SiteResponse
from app.schemas.operator import OperatorResponse
from app.schemas.audit import AuditEventResponse


class RentalBase(BaseModel):
    equipment_id: str
    site_id: Optional[str] = None
    operator_id: Optional[str] = None
    checked_out_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
    daily_rate: float
    condition_notes: Optional[str] = None


class RentalResponse(RentalBase):
    id: int
    created_at: datetime
    updated_at: datetime
    site: Optional[SiteResponse] = None
    operator: Optional[OperatorResponse] = None

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    equipment_id: str
    site_id: str
    operator_id: str
    due_at: datetime
    daily_rate: Optional[float] = None
    condition_notes: Optional[str] = None
    actor: Optional[str] = "Operator"


class CheckoutResponse(BaseModel):
    success: bool = True
    equipment_id: str
    status: str
    rental: RentalResponse
    audit_event: AuditEventResponse


class CheckinRequest(BaseModel):
    equipment_id: str
    condition: Optional[str] = "Good"
    notes: Optional[str] = None
    actor: Optional[str] = "Operator"


class CheckinResponse(BaseModel):
    success: bool = True
    equipment_id: str
    status: str
    rental: RentalResponse
    audit_event: AuditEventResponse
