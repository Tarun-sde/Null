"""
Tests for authentication endpoints: login, logout, me, and protected route enforcement.
Uses the SQLite in-memory test database (via TestClient default settings).
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal, engine
from app.models import Base
from app.models.user import User
from app.core.security import hash_password

# Test credentials
TEST_EMAIL = "testadmin@rentsense.test"
TEST_PASSWORD = "TestPass123!"

client = TestClient(app, raise_server_exceptions=True)


@pytest.fixture(autouse=True, scope="module")
def setup_test_user():
    """Create a test user once for all auth tests, clean up after."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == TEST_EMAIL).first()
        if not existing:
            user = User(
                email=TEST_EMAIL,
                hashed_password=hash_password(TEST_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

    yield

    # Cleanup
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == TEST_EMAIL).delete()
        db.commit()
    finally:
        db.close()


def test_login_valid_credentials():
    resp = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == TEST_EMAIL
    assert body["role"] == "admin"
    # Cookie must be set
    assert "access_token" in resp.cookies


def test_login_invalid_password():
    resp = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": "wrong"})
    assert resp.status_code == 401
    assert "Invalid" in resp.json()["message"]


def test_login_unknown_email():
    resp = client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "x"})
    assert resp.status_code == 401


def test_me_while_authenticated():
    # Login first
    login_resp = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert login_resp.status_code == 200
    token = login_resp.cookies.get("access_token")

    me_resp = client.get("/api/v1/auth/me", cookies={"access_token": token})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == TEST_EMAIL


def test_me_without_session():
    # Use a fresh client with no cookies to ensure no lingering session
    from fastapi.testclient import TestClient as FreshClient
    fresh = FreshClient(app, raise_server_exceptions=True)
    resp = fresh.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_logout():
    login_resp = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    token = login_resp.cookies.get("access_token")

    logout_resp = client.post("/api/v1/auth/logout", cookies={"access_token": token})
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "logged_out"


def test_protected_checkout_without_auth():
    """Rental checkout requires auth — should return 401 without cookie."""
    resp = client.post(
        "/api/v1/rentals/checkout",
        json={
            "equipment_id": "EQX1007",
            "site_id": "SITE-001",
            "operator_id": "OP-001",
            "due_at": "2026-12-01T00:00:00Z",
        },
    )
    assert resp.status_code == 401


def test_protected_checkout_with_auth():
    """With a valid session cookie, checkout should be processable (may fail for business reasons but not auth)."""
    login_resp = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    token = login_resp.cookies.get("access_token")

    resp = client.post(
        "/api/v1/rentals/checkout",
        json={
            "equipment_id": "EQX1007",
            "site_id": "SITE-001",
            "operator_id": "OP-001",
            "due_at": "2026-12-01T00:00:00Z",
        },
        cookies={"access_token": token},
    )
    # 201 = success, 409 = already checked out, both are valid business responses (not 401)
    assert resp.status_code in (200, 201, 409)
