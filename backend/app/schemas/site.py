from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SiteBase(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    latitude: float
    longitude: float


class SiteResponse(SiteBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
