from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class TelemetryIngestRequest(BaseModel):
    equipment_id: str
    timestamp: Optional[datetime] = None
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180")
    engine_hours: float = Field(..., ge=0.0, description="Total engine runtime hours >= 0")
    idle_hours: float = Field(..., ge=0.0, description="Total idle runtime hours >= 0")
    fuel_pct: float = Field(..., ge=0.0, le=100.0, description="Fuel level percentage between 0 and 100")

    @field_validator("idle_hours")
    @classmethod
    def validate_idle_hours(cls, v: float, info) -> float:
        engine_hours = info.data.get("engine_hours")
        if engine_hours is not None and v > engine_hours + 0.001:
            raise ValueError("idle_hours cannot exceed total engine_hours")
        return v


class TelemetryStreamEvent(BaseModel):
    equipment_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    engine_hours: float
    idle_hours: float
    fuel_pct: float
    utilization_rate: float
    status: str
