from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class ForecastBase(BaseModel):
    site_id: Optional[str] = None
    equipment_type: str
    forecast_date: datetime
    predicted_units: float
    confidence: float
    backtest_error: Optional[float] = None
    drivers: Optional[Dict[str, Any]] = None


class ForecastResponse(ForecastBase):
    id: int
    site_name: Optional[str] = None
    explanation: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ForecastFleetSummary(BaseModel):
    total_forecasted_units: float
    avg_confidence: float
    avg_backtest_error: Optional[float] = None
    horizon_weeks: int
    forecasts: List[ForecastResponse]
