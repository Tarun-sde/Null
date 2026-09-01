from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Equipment, Rental, Telemetry, Alert, AuditEvent
from app.services.status_service import derive_status, calculate_utilization, EquipmentStatus
from app.schemas.equipment import EquipmentListItem, EquipmentDetailResponse
from app.schemas.rental import RentalResponse
from app.schemas.site import SiteResponse
from app.schemas.operator import OperatorResponse
from app.schemas.telemetry import TelemetryResponse
from app.schemas.alert import AlertResponse
from app.schemas.audit import AuditEventResponse


def get_current_rental(equipment: Equipment) -> Optional[Rental]:
    """Get the currently open/active rental for an equipment asset."""
    for rental in equipment.rentals:
        if rental.checked_in_at is None:
            return rental
    return None


def get_latest_telemetry(equipment: Equipment) -> Optional[Telemetry]:
    """Get the most recent telemetry record for an equipment asset."""
    if equipment.telemetry:
        return equipment.telemetry[0]
    return None


def build_equipment_list_item(equipment: Equipment) -> EquipmentListItem:
    """Transform an Equipment ORM object into an enriched EquipmentListItem schema."""
    current_rental = get_current_rental(equipment)
    latest_telemetry = get_latest_telemetry(equipment)
    status = derive_status(current_rental, latest_telemetry)

    utilization_rate = 0.0
    if latest_telemetry:
        utilization_rate = calculate_utilization(
            latest_telemetry.engine_hours, latest_telemetry.idle_hours
        )

    site_resp = None
    op_resp = None
    rental_resp = None

    if current_rental:
        if current_rental.site:
            site_resp = SiteResponse.model_validate(current_rental.site)
        if current_rental.operator:
            op_resp = OperatorResponse.model_validate(current_rental.operator)
        rental_resp = RentalResponse.model_validate(current_rental)

    telem_resp = None
    if latest_telemetry:
        telem_resp = TelemetryResponse.model_validate(latest_telemetry)

    return EquipmentListItem(
        id=equipment.id,
        type=equipment.type,
        dealer=equipment.dealer,
        daily_rate=equipment.daily_rate,
        status=status.value,
        current_rental=rental_resp,
        site=site_resp,
        operator=op_resp,
        latest_telemetry=telem_resp,
        utilization_rate=round(utilization_rate, 4),
        metadata_json=equipment.metadata_json,
        created_at=equipment.created_at,
        updated_at=equipment.updated_at,
    )


def build_equipment_detail(equipment: Equipment) -> EquipmentDetailResponse:
    """Transform an Equipment ORM object into an enriched EquipmentDetailResponse schema."""
    current_rental = get_current_rental(equipment)
    latest_telemetry = get_latest_telemetry(equipment)
    status = derive_status(current_rental, latest_telemetry)

    utilization_rate = 0.0
    if latest_telemetry:
        utilization_rate = calculate_utilization(
            latest_telemetry.engine_hours, latest_telemetry.idle_hours
        )

    site_resp = None
    op_resp = None
    rental_resp = None

    if current_rental:
        if current_rental.site:
            site_resp = SiteResponse.model_validate(current_rental.site)
        if current_rental.operator:
            op_resp = OperatorResponse.model_validate(current_rental.operator)
        rental_resp = RentalResponse.model_validate(current_rental)

    telem_resp = None
    if latest_telemetry:
        telem_resp = TelemetryResponse.model_validate(latest_telemetry)

    recent_telemetry = [TelemetryResponse.model_validate(t) for t in equipment.telemetry[:20]]
    rental_history = [RentalResponse.model_validate(r) for r in equipment.rentals]
    active_alerts = [AlertResponse.model_validate(a) for a in equipment.alerts if a.status == "OPEN"]
    audit_timeline = [AuditEventResponse.model_validate(ae) for ae in equipment.audit_events]

    return EquipmentDetailResponse(
        id=equipment.id,
        type=equipment.type,
        dealer=equipment.dealer,
        daily_rate=equipment.daily_rate,
        status=status.value,
        current_rental=rental_resp,
        site=site_resp,
        operator=op_resp,
        latest_telemetry=telem_resp,
        recent_telemetry=recent_telemetry,
        rental_history=rental_history,
        active_alerts=active_alerts,
        audit_timeline=audit_timeline,
        utilization_rate=round(utilization_rate, 4),
        metadata_json=equipment.metadata_json,
        created_at=equipment.created_at,
        updated_at=equipment.updated_at,
    )
