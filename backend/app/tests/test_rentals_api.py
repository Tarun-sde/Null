from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from main import app
from app.db.session import SessionLocal
from app.seed.seed import seed_database
from app.models import Rental, AuditEvent, Equipment

client = TestClient(app)


def setup_module():
    db = SessionLocal()
    try:
        seed_database(db, reset=True)
    finally:
        db.close()


def test_checkout_unknown_equipment(auth_client):
    payload = {
        "equipment_id": "EQX_UNKNOWN_999",
        "site_id": "SITE-001",
        "operator_id": "OP-001",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }
    response = auth_client.post("/api/v1/rentals/checkout", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_checkout_unknown_site(auth_client):
    payload = {
        "equipment_id": "EQX1007",
        "site_id": "SITE_UNKNOWN_999",
        "operator_id": "OP-001",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }
    response = auth_client.post("/api/v1/rentals/checkout", json=payload)
    assert response.status_code == 404
    assert "site" in response.json()["detail"].lower()


def test_checkout_unknown_operator(auth_client):
    payload = {
        "equipment_id": "EQX1007",
        "site_id": "SITE-001",
        "operator_id": "OP_UNKNOWN_999",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }
    response = auth_client.post("/api/v1/rentals/checkout", json=payload)
    assert response.status_code == 404
    assert "operator" in response.json()["detail"].lower()


def test_checkout_already_rented_equipment(auth_client):
    # EQX1001 is already rented at SITE-001
    payload = {
        "equipment_id": "EQX1001",
        "site_id": "SITE-002",
        "operator_id": "OP-002",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    }
    response = auth_client.post("/api/v1/rentals/checkout", json=payload)
    assert response.status_code == 409
    assert "already has an active rental" in response.json()["detail"].lower() or "already checked out" in response.json()["detail"].lower()


def test_checkout_success_and_audit(auth_client):
    # EQX1007 is unassigned in yard
    now = datetime.now(timezone.utc)
    due = now + timedelta(days=7)
    payload = {
        "equipment_id": "EQX1007",
        "site_id": "SITE-002",
        "operator_id": "OP-003",
        "due_at": due.isoformat(),
        "daily_rate": 420.0,
        "condition_notes": "Clean pickup for logistics foundation",
        "actor": "Marcus Vance",
    }
    response = auth_client.post("/api/v1/rentals/checkout", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["equipment_id"] == "EQX1007"
    assert data["status"] == "ACTIVE"
    assert data["rental"]["site"]["id"] == "SITE-002"
    assert data["rental"]["operator"]["id"] == "OP-003"
    assert data["rental"]["checked_in_at"] is None
    assert data["audit_event"]["event_type"] == "CHECKOUT"
    assert data["audit_event"]["actor"] == "Marcus Vance"

    # Verify in DB
    db = SessionLocal()
    try:
        active_rental = (
            db.query(Rental)
            .filter(Rental.equipment_id == "EQX1007", Rental.checked_in_at.is_(None))
            .first()
        )
        assert active_rental is not None
        assert active_rental.site_id == "SITE-002"
        assert active_rental.operator_id == "OP-003"

        audit = (
            db.query(AuditEvent)
            .filter(AuditEvent.equipment_id == "EQX1007", AuditEvent.event_type == "CHECKOUT")
            .order_by(AuditEvent.id.desc())
            .first()
        )
        assert audit is not None
        assert audit.actor == "Marcus Vance"
    finally:
        db.close()


def test_checkin_unknown_equipment(auth_client):
    payload = {
        "equipment_id": "EQX_UNKNOWN_999",
        "condition": "Good",
    }
    response = auth_client.post("/api/v1/rentals/checkin", json=payload)
    assert response.status_code == 404


def test_checkin_equipment_without_active_rental():
    pass


def test_checkin_success_and_audit(auth_client):
    # Check in EQX1007 which was checked out above
    payload = {
        "equipment_id": "EQX1007",
        "condition": "Good",
        "notes": "Returned clean, full fuel tank",
        "actor": "Elena Rostova",
    }
    response = auth_client.post("/api/v1/rentals/checkin", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["equipment_id"] == "EQX1007"
    assert data["status"] == "UNASSIGNED"
    assert data["rental"]["checked_in_at"] is not None
    assert "Good" in data["rental"]["condition_notes"]
    assert data["audit_event"]["event_type"] == "CHECKIN"
    assert data["audit_event"]["actor"] == "Elena Rostova"

    # Now trying to check in again should fail with 409
    repeat_response = auth_client.post("/api/v1/rentals/checkin", json=payload)
    assert repeat_response.status_code == 409
    assert "does not have an active rental" in repeat_response.json()["detail"].lower()


def test_sites_and_operators_endpoints():
    sites_res = client.get("/api/v1/sites")
    assert sites_res.status_code == 200
    assert len(sites_res.json()) >= 3

    ops_res = client.get("/api/v1/operators")
    assert ops_res.status_code == 200
    assert len(ops_res.json()) >= 4
