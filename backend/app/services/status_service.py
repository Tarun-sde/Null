from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from app.core.config import settings


class EquipmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    DUE_SOON = "DUE_SOON"
    OVERDUE = "OVERDUE"
    UNASSIGNED = "UNASSIGNED"


def calculate_utilization(engine_hours: float, idle_hours: float) -> float:
    """
    Calculate equipment utilization rate: (engine_hours - idle_hours) / engine_hours.
    Returns 0.0 if engine_hours is 0.
    """
    if engine_hours <= 0:
        return 0.0
    active_hours = max(0.0, engine_hours - idle_hours)
    return round(active_hours / engine_hours, 4)



def derive_status(
    rental: Optional[object] = None,
    telemetry: Optional[object] = None,
    now: Optional[datetime] = None,
) -> EquipmentStatus:
    """
    Derive the single source-of-truth status for an equipment asset.

    Deterministic Precedence Hierarchy:
    1. UNASSIGNED:
       - No active rental exists (rental is None or checked_in_at is set).
       - Open rental exists but lacks site_id or operator_id (missing assignment scenario).
    2. OVERDUE:
       - Active assigned rental exists and current time exceeds due_at.
    3. DUE_SOON:
       - Active assigned rental exists and remaining time until due_at <= ALERT_DUE_SOON_HOURS (48h).
    4. IDLE:
       - Active assigned rental exists, not overdue/due soon, but telemetry indicates:
         a) idle_hours >= IDLE_HOURS_THRESHOLD (8h), OR
         b) utilization < LOW_UTILIZATION_THRESHOLD (0.20 / 20%).
    5. ACTIVE:
       - Active assigned rental with normal operational utilization within schedule.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    # 1. Unassigned Check: No active rental or missing assignment
    if rental is None:
        return EquipmentStatus.UNASSIGNED

    checked_in_at = getattr(rental, "checked_in_at", None)
    if checked_in_at is not None:
        return EquipmentStatus.UNASSIGNED

    site_id = getattr(rental, "site_id", None)
    operator_id = getattr(rental, "operator_id", None)
    if not site_id or not operator_id:
        return EquipmentStatus.UNASSIGNED

    # 2. Overdue & Due Soon Checks
    due_at = getattr(rental, "due_at", None)
    if due_at is not None:
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=timezone.utc)

        if now > due_at:
            return EquipmentStatus.OVERDUE

        time_remaining = due_at - now
        due_soon_threshold_seconds = settings.ALERT_DUE_SOON_HOURS * 3600
        if 0 <= time_remaining.total_seconds() <= due_soon_threshold_seconds:
            return EquipmentStatus.DUE_SOON

    # 3. Telemetry & Utilization Checks (IDLE vs ACTIVE)
    if telemetry is not None:
        engine_hours = float(getattr(telemetry, "engine_hours", 0.0) or 0.0)
        idle_hours = float(getattr(telemetry, "idle_hours", 0.0) or 0.0)

        # Check idle hours threshold (default 8.0h)
        if idle_hours >= settings.IDLE_HOURS_THRESHOLD:
            return EquipmentStatus.IDLE

        # Check utilization rate if equipment has engine hours recorded
        if engine_hours > 0:
            utilization = calculate_utilization(engine_hours, idle_hours)
            if utilization < settings.LOW_UTILIZATION_THRESHOLD:
                return EquipmentStatus.IDLE

    # 4. Default Assigned Operational Status
    return EquipmentStatus.ACTIVE
