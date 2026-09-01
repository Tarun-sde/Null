from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Equipment
from app.schemas.equipment import EquipmentListItem, EquipmentDetailResponse
from app.services.equipment_service import build_equipment_list_item, build_equipment_detail

router = APIRouter(prefix="/equipment", tags=["Equipment"])


@router.get("", response_model=List[EquipmentListItem])
def list_equipment(
    search: Optional[str] = Query(None, description="Search term for ID, type, or dealer"),
    status: Optional[str] = Query(None, description="Filter by derived status (ACTIVE, IDLE, DUE_SOON, OVERDUE, UNASSIGNED)"),
    site_id: Optional[str] = Query(None, description="Filter by current assigned site ID"),
    type: Optional[str] = Query(None, description="Filter by equipment type"),
    db: Session = Depends(get_db),
):
    """
    Retrieve fleet equipment assets with real-time derived operational status,
    latest telemetry, and current rental assignment details.
    """
    query = db.query(Equipment)

    if type:
        query = query.filter(Equipment.type.ilike(f"%{type}%"))

    equipment_records = query.all()
    results: List[EquipmentListItem] = []

    for eq in equipment_records:
        item = build_equipment_list_item(eq)

        # Apply search filter across ID, type, dealer, or metadata model
        if search:
            s = search.lower()
            model_name = ""
            if eq.metadata_json and isinstance(eq.metadata_json, dict):
                model_name = str(eq.metadata_json.get("model", "")).lower()
            matches = (
                s in eq.id.lower()
                or s in eq.type.lower()
                or s in eq.dealer.lower()
                or s in model_name
            )
            if not matches:
                continue

        # Apply site filter
        if site_id:
            if not item.site or item.site.id != site_id:
                continue

        # Apply status filter
        if status:
            if item.status.upper() != status.upper():
                continue

        results.append(item)

    return results


@router.get("/{id}", response_model=EquipmentDetailResponse)
def get_equipment_detail(
    id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve comprehensive equipment details by ID including current rental,
    latest telemetry, recent telemetry history, full rental history, active alerts,
    and audit event timeline.
    """
    equipment = db.query(Equipment).filter(Equipment.id == id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment with ID '{id}' not found",
        )

    return build_equipment_detail(equipment)
