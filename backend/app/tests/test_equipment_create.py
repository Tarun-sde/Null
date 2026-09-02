"""
Tests for POST /api/v1/equipment (Add Equipment).
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal, engine
from app.models import Base, Equipment
from app.models.user import User
from app.core.security import hash_password

TEST_EMAIL = "eqtest@rentsense.test"
TEST_PASSWORD = "EqPass456!"
TEST_EQ_ID = "EQXTEST99"

client = TestClient(app, raise_server_exceptions=True)


@pytest.fixture(autouse=True, scope="module")
def setup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == TEST_EMAIL).first():
            db.add(User(
                email=TEST_EMAIL,
                hashed_password=hash_password(TEST_PASSWORD),
                role="admin",
                is_active=True,
            ))
            db.commit()
        # Ensure test equipment doesn't pre-exist
        db.query(Equipment).filter(Equipment.id == TEST_EQ_ID).delete()
        db.commit()
    finally:
        db.close()

    yield

    # Cleanup: remove test equipment
    db = SessionLocal()
    try:
        db.query(Equipment).filter(Equipment.id == TEST_EQ_ID).delete()
        db.query(User).filter(User.email == TEST_EMAIL).delete()
        db.commit()
    finally:
        db.close()


def _auth_cookie():
    resp = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    return {"access_token": resp.cookies.get("access_token")}


def test_create_equipment_without_auth():
    resp = client.post("/api/v1/equipment", json={
        "id": TEST_EQ_ID, "type": "Excavator", "dealer": "Cat Rentals", "daily_rate": 300.0
    })
    assert resp.status_code == 401


def test_create_equipment_missing_required_fields():
    resp = client.post("/api/v1/equipment", json={"id": TEST_EQ_ID}, cookies=_auth_cookie())
    assert resp.status_code == 422


def test_create_equipment_success():
    resp = client.post("/api/v1/equipment", json={
        "id": TEST_EQ_ID,
        "type": "Excavator",
        "dealer": "Test Rentals",
        "daily_rate": 350.0,
        "model": "TEST-X100",
        "serial": "TST-0001",
    }, cookies=_auth_cookie())
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == TEST_EQ_ID
    assert body["type"] == "Excavator"
    assert body["metadata_json"]["qr_code"] == TEST_EQ_ID
    assert body["metadata_json"]["model"] == "TEST-X100"


def test_create_equipment_duplicate_id():
    resp = client.post("/api/v1/equipment", json={
        "id": TEST_EQ_ID,
        "type": "Bulldozer",
        "dealer": "Other Rentals",
        "daily_rate": 500.0,
    }, cookies=_auth_cookie())
    assert resp.status_code == 409


def test_new_equipment_appears_in_list():
    resp = client.get("/api/v1/equipment")
    assert resp.status_code == 200
    ids = [eq["id"] for eq in resp.json()]
    assert TEST_EQ_ID in ids


def test_new_equipment_detail_works():
    resp = client.get(f"/api/v1/equipment/{TEST_EQ_ID}")
    assert resp.status_code == 200
    assert resp.json()["id"] == TEST_EQ_ID


def test_new_equipment_qr_lookup():
    """Simulate QR scan: look up by ID — same mechanism the scan page uses."""
    resp = client.get(f"/api/v1/equipment/{TEST_EQ_ID}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata_json"]["qr_code"] == TEST_EQ_ID
