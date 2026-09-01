from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.site import SiteResponse
from app.schemas.operator import OperatorResponse


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
