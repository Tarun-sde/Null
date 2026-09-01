from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    equipment_id: str
    alert_type: str
    severity: str
    message: str
    status: str
    metadata_json: Optional[Dict[str, Any]] = None


class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
