from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Equipment, Site, Operator, Rental, AuditEvent
from app.schemas.rental import (
    CheckoutRequest,
    CheckoutResponse,
    CheckinRequest,
    CheckinResponse,
    RentalResponse,
)
from app.schemas.audit import AuditEventResponse
from app.schemas.site import SiteResponse
from app.schemas.operator import OperatorResponse
from app.services.status_service import derive_status
from app.services.equipment_service import get_latest_telemetry

router = APIRouter(prefix="/rentals", tags=["Rentals"])


@router.post("/checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def checkout_equipment(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
):
    """
    Check out an equipment asset to a construction site and operator.
    Validates equipment existence, site, operator, and confirms no active rental exists.
    Creates an atomic Rental record, AuditEvent, and recalculates derived status.
    """
    # 1. Validate Equipment
    equipment = db.query(Equipment).filter(Equipment.id == payload.equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment with ID '{payload.equipment_id}' not found",
        )

    # 2. Validate Site
    site = db.query(Site).filter(Site.id == payload.site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with ID '{payload.site_id}' not found",
        )

    # 3. Validate Operator
    operator = db.query(Operator).filter(Operator.id == payload.operator_id).first()
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operator with ID '{payload.operator_id}' not found",
        )

    # 4. Check for active open rental
    active_rental = (
        db.query(Rental)
        .filter(Rental.equipment_id == equipment.id, Rental.checked_in_at.is_(None))
        .first()
    )
    if active_rental:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Equipment '{equipment.id}' is already checked out under active rental #{active_rental.id}",
        )

    # 5. Create Rental and AuditEvent atomically
    now = datetime.now(timezone.utc)
    due_at = payload.due_at
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)

    daily_rate = payload.daily_rate if payload.daily_rate is not None else equipment.daily_rate

    try:
        new_rental = Rental(
            equipment_id=equipment.id,
            site_id=site.id,
            operator_id=operator.id,
            checked_out_at=now,
            due_at=due_at,
            checked_in_at=None,
            daily_rate=daily_rate,
            condition_notes=payload.condition_notes,
            created_at=now,
        )
        db.add(new_rental)
        db.flush()

        audit_event = AuditEvent(
            event_type="CHECKOUT",
            equipment_id=equipment.id,
            actor=payload.actor or "Operator",
            timestamp=now,
            metadata_json={
                "rental_id": new_rental.id,
                "site_id": site.id,
                "site_name": site.name,
                "operator_id": operator.id,
                "operator_name": operator.name,
                "due_at": due_at.isoformat(),
                "daily_rate": daily_rate,
            },
        )
        db.add(audit_event)
        db.commit()
        db.refresh(new_rental)
        db.refresh(audit_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process checkout transaction: {str(e)}",
        )

    # 6. Recalculate derived status
    latest_telemetry = get_latest_telemetry(equipment)
    derived_status = derive_status(new_rental, latest_telemetry, now=now)

    # 7. Construct enriched response
    rental_resp = RentalResponse(
        id=new_rental.id,
        equipment_id=new_rental.equipment_id,
        site_id=new_rental.site_id,
        operator_id=new_rental.operator_id,
        checked_out_at=new_rental.checked_out_at,
        due_at=new_rental.due_at,
        checked_in_at=new_rental.checked_in_at,
        daily_rate=new_rental.daily_rate,
        condition_notes=new_rental.condition_notes,
        created_at=new_rental.created_at,
        updated_at=new_rental.updated_at,
        site=SiteResponse.model_validate(site),
        operator=OperatorResponse.model_validate(operator),
    )

    audit_resp = AuditEventResponse.model_validate(audit_event)

    return CheckoutResponse(
        success=True,
        equipment_id=equipment.id,
        status=derived_status.value,
        rental=rental_resp,
        audit_event=audit_resp,
    )


@router.post("/checkin", response_model=CheckinResponse, status_code=status.HTTP_200_OK)
def checkin_equipment(
    payload: CheckinRequest,
    db: Session = Depends(get_db),
):
    """
    Check in an active rental, record equipment return condition,
    create an immutable CHECKIN AuditEvent, and recalculate derived status.
    """
    # 1. Validate Equipment
    equipment = db.query(Equipment).filter(Equipment.id == payload.equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment with ID '{payload.equipment_id}' not found",
        )

    # 2. Validate Active Rental
    active_rental = (
        db.query(Rental)
        .filter(Rental.equipment_id == equipment.id, Rental.checked_in_at.is_(None))
        .first()
    )
    if not active_rental:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Equipment '{equipment.id}' does not have an active rental to check in",
        )

    now = datetime.now(timezone.utc)
    notes_text = f"Condition: {payload.condition or 'Good'}"
    if payload.notes:
        notes_text += f" | Notes: {payload.notes}"

    try:
        active_rental.checked_in_at = now
        active_rental.condition_notes = notes_text

        audit_event = AuditEvent(
            event_type="CHECKIN",
            equipment_id=equipment.id,
            actor=payload.actor or "Operator",
            timestamp=now,
            metadata_json={
                "rental_id": active_rental.id,
                "site_id": active_rental.site_id,
                "condition": payload.condition or "Good",
                "notes": payload.notes,
            },
        )
        db.add(audit_event)
        db.commit()
        db.refresh(active_rental)
        db.refresh(audit_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process check-in transaction: {str(e)}",
        )

    # 3. Recalculate derived status (now rental is closed -> UNASSIGNED)
    latest_telemetry = get_latest_telemetry(equipment)
    derived_status = derive_status(None, latest_telemetry, now=now)

    site_resp = SiteResponse.model_validate(active_rental.site) if active_rental.site else None
    op_resp = OperatorResponse.model_validate(active_rental.operator) if active_rental.operator else None

    rental_resp = RentalResponse(
        id=active_rental.id,
        equipment_id=active_rental.equipment_id,
        site_id=active_rental.site_id,
        operator_id=active_rental.operator_id,
        checked_out_at=active_rental.checked_out_at,
        due_at=active_rental.due_at,
        checked_in_at=active_rental.checked_in_at,
        daily_rate=active_rental.daily_rate,
        condition_notes=active_rental.condition_notes,
        created_at=active_rental.created_at,
        updated_at=active_rental.updated_at,
        site=site_resp,
        operator=op_resp,
    )

    audit_resp = AuditEventResponse.model_validate(audit_event)

    return CheckinResponse(
        success=True,
        equipment_id=equipment.id,
        status=derived_status.value,
        rental=rental_resp,
        audit_event=audit_resp,
    )
