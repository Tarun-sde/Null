import os
import sys
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal
from app.models import Action, Alert, Rental, AuditEvent, Equipment, ImpactRecord
from app.seed.seed import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    db = SessionLocal()
    seed_database(db, reset=True)
    yield
    db.close()


def test_create_action_success(auth_client):
    res = auth_client.post(
        "/api/v1/actions",
        json={
            "equipment_id": "EQX1001",
            "action_type": "REASSIGN",
            "priority": "HIGH",
            "notes": "Reassigning to Highland Medical",
            "actor": "Marcus Vance",
            "payload": {"target_site_id": "SITE-003"},
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["equipment_id"] == "EQX1001"
    assert data["action_type"] == "REASSIGN"
    assert data["status"] == "PENDING"
    assert data["priority"] == "HIGH"


def test_create_action_invalid_type_rejected(auth_client):
    res = auth_client.post(
        "/api/v1/actions",
        json={
            "equipment_id": "EQX1001",
            "action_type": "INVALID_ACTION_TYPE",
        },
    )
    assert res.status_code == 400


def test_create_action_unknown_equipment_rejected(auth_client):
    res = auth_client.post(
        "/api/v1/actions",
        json={
            "equipment_id": "UNKNOWN_999",
            "action_type": "RETURN",
        },
    )
    assert res.status_code == 400


def test_complete_return_action_closes_rental_resolves_alert_and_records_impact(auth_client):
    db = SessionLocal()
    # EQX1006 is overdue
    res_create = auth_client.post(
        "/api/v1/actions",
        json={
            "equipment_id": "EQX1006",
            "action_type": "RETURN",
            "priority": "CRITICAL",
            "notes": "Returned overdue lift to depot",
            "actor": "Marcus Vance",
        },
    )
    assert res_create.status_code == 201
    action_id = res_create.json()["id"]

    # Verify alert exists and is OPEN before completion
    alert_before = db.query(Alert).filter(Alert.equipment_id == "EQX1006", Alert.status == "OPEN").first()
    assert alert_before is not None

    # Complete action
    res_complete = auth_client.post(
        f"/api/v1/actions/{action_id}/complete",
        json={
            "notes": "Off-rent physical inspection complete, zero damage",
            "actor": "Marcus Vance",
        },
    )
    assert res_complete.status_code == 200
    completed_data = res_complete.json()
    assert completed_data["status"] == "COMPLETED"
    assert completed_data["completed_at"] is not None

    # Verify rental was closed in database
    db.expire_all()
    rental = db.query(Rental).filter(Rental.equipment_id == "EQX1006", Rental.checked_in_at.isnot(None)).first()
    assert rental is not None
    assert rental.checked_in_at is not None

    # Verify alert is now RESOLVED
    alert_after = db.query(Alert).filter(Alert.equipment_id == "EQX1006", Alert.status == "OPEN").first()
    assert alert_after is None

    # Verify audit event exists
    audit = db.query(AuditEvent).filter(AuditEvent.equipment_id == "EQX1006", AuditEvent.event_type == "RETURN_COMPLETED").first()
    assert audit is not None
    assert audit.actor == "Marcus Vance"

    # Verify Realized Savings Impact record created
    impact = db.query(ImpactRecord).filter(ImpactRecord.action_id == action_id).first()
    assert impact is not None
    assert impact.realized_amount > 0
    assert impact.currency == "INR"
    db.close()


def test_complete_reassign_action_updates_site_and_resolves_alerts(auth_client):
    db = SessionLocal()
    res_create = auth_client.post(
        "/api/v1/actions",
        json={
            "equipment_id": "EQX1001",
            "action_type": "REASSIGN",
            "priority": "HIGH",
            "notes": "Dispatching to Highland Medical",
            "actor": "Marcus Vance",
        },
    )
    action_id = res_create.json()["id"]

    res_complete = auth_client.post(
        f"/api/v1/actions/{action_id}/complete",
        json={
            "notes": "Reassigned to Highland Medical Center",
            "payload": {"target_site_id": "SITE-003"},
        },
    )
    assert res_complete.status_code == 200
    assert res_complete.json()["status"] == "COMPLETED"

    # Verify rental site updated
    db.expire_all()
    rental = db.query(Rental).filter(Rental.equipment_id == "EQX1001", Rental.checked_in_at.is_(None)).first()
    assert rental is not None
    assert rental.site_id == "SITE-003"

    # Verify audit event
    audit = db.query(AuditEvent).filter(AuditEvent.equipment_id == "EQX1001", AuditEvent.event_type == "EQUIPMENT_REASSIGNED").first()
    assert audit is not None

    # Verify Realized Impact Record
    impact = db.query(ImpactRecord).filter(ImpactRecord.action_id == action_id).first()
    assert impact is not None
    assert impact.realized_amount == 18500.0 * 3.0  # ₹55,500 realized savings
    db.close()


def test_complete_action_idempotency_error(auth_client):
    res_create = auth_client.post(
        "/api/v1/actions",
        json={"equipment_id": "EQX1001", "action_type": "INVESTIGATE"},
    )
    action_id = res_create.json()["id"]

    res_1 = auth_client.post(f"/api/v1/actions/{action_id}/complete", json={})
    assert res_1.status_code == 200

    # Second completion attempt should fail
    res_2 = auth_client.post(f"/api/v1/actions/{action_id}/complete", json={})
    assert res_2.status_code == 400


def test_cancel_action(auth_client):
    res_create = auth_client.post(
        "/api/v1/actions",
        json={"equipment_id": "EQX1001", "action_type": "REASSIGN"},
    )
    action_id = res_create.json()["id"]

    res_cancel = auth_client.post(
        f"/api/v1/actions/{action_id}/cancel",
        json={"reason": "Jobsite requested cancellation"},
    )
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"

    # Trying to complete cancelled action should fail
    res_comp = auth_client.post(f"/api/v1/actions/{action_id}/complete", json={})
    assert res_comp.status_code == 400


def test_manual_alert_resolve_endpoint(auth_client):
    db = SessionLocal()
    open_alert = db.query(Alert).filter(Alert.status == "OPEN").first()
    assert open_alert is not None
    alert_id = open_alert.id

    res_resolve = auth_client.post(
        f"/api/v1/alerts/{alert_id}/resolve",
        json={
            "resolution_notes": "Operator inspected and cleared alert",
            "actor": "Marcus Vance",
        },
    )
    assert res_resolve.status_code == 200
    assert res_resolve.json()["status"] == "RESOLVED"

    db.expire_all()
    updated = db.query(Alert).filter(Alert.id == alert_id).first()
    assert updated.status == "RESOLVED"
    assert updated.resolved_at is not None
    db.close()
