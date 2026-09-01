from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class OperatorBase(BaseModel):
    id: str
    name: str
    contact: Optional[str] = None


class OperatorResponse(OperatorBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
