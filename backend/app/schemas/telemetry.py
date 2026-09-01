from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TelemetryBase(BaseModel):
    equipment_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    engine_hours: float
    idle_hours: float
    fuel_pct: float


class TelemetryResponse(TelemetryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
