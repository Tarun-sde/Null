from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


class AuditEventBase(BaseModel):
    event_type: str
    equipment_id: Optional[str] = None
    actor: Optional[str] = None
    timestamp: datetime
    metadata_json: Optional[Dict[str, Any]] = None


class AuditEventResponse(AuditEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
