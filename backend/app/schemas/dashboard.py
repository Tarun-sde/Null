from typing import Dict
from pydantic import BaseModel


class DashboardKPIResponse(BaseModel):
    total_equipment: int
    active: int
    idle: int
    due_soon: int
    overdue: int
    unassigned: int
    status_counts: Dict[str, int]
    open_alerts: int
    fleet_utilization_pct: float
