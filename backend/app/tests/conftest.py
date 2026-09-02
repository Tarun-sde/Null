"""
Shared pytest fixtures for the RentSense test suite.
Provides an authenticated TestClient that tests using protected endpoints can use.
"""
import pytest
from fastapi.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password, create_access_token

_TEST_ID = "00000000-0000-0000-0000-000000000002"
_TEST_EMAIL = "ci-test@rentsense.test"
_TEST_PASSWORD = "CiTest789!"


def _ensure_test_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == _TEST_ID).first()
        if not user:
            db.add(User(
                id=_TEST_ID,
                email=_TEST_EMAIL,
                hashed_password=hash_password(_TEST_PASSWORD),
                role="admin",
                is_active=True,
            ))
            db.commit()
    finally:
        db.close()


@pytest.fixture
def auth_client():
    """A TestClient pre-authenticated with a test admin user (function scoped)."""
    _ensure_test_user()
    token = create_access_token({"sub": _TEST_ID, "email": _TEST_EMAIL, "role": "admin"})
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set("access_token", token)
    return c
