import os
import sys
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal
from app.models import ImpactRecord, Action, Equipment
from app.analytics.impact_engine import (
    calculate_action_impact_estimate,
    record_realized_action_savings,
    get_fleet_impact_summary,
)
from app.seed.seed import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    db = SessionLocal()
    seed_database(db, reset=True)
    yield
    db.close()


def test_calculate_action_impact_estimate():
    db = SessionLocal()
    eq1 = db.query(Equipment).filter(Equipment.id == "EQX1001").first()
    
    est = calculate_action_impact_estimate(
        equipment=eq1,
        action_type="REASSIGN",
        telemetry_idle_hours=14.2,
    )
    assert est["impact_type"] == "IDLE_AVOIDANCE"
    assert est["daily_rate"] == 18500.0
    assert est["estimated_amount"] == 33300.0  # 1.8 days * 18500
    assert est["currency"] == "INR"
    db.close()


def test_non_negative_impact_protection():
    db = SessionLocal()
    eq = db.query(Equipment).first()
    est = calculate_action_impact_estimate(
        equipment=eq,
        action_type="RETURN",
        overdue_hours=-10.0,
    )
    assert est["estimated_amount"] >= 0.0
    db.close()


def test_get_fleet_impact_summary_api(auth_client):
    # First complete an action to generate realized savings
    res_action = auth_client.post(
        "/api/v1/actions",
        json={"equipment_id": "EQX1001", "action_type": "REASSIGN"},
    )
    action_id = res_action.json()["id"]
    auth_client.post(f"/api/v1/actions/{action_id}/complete", json={"payload": {"target_site_id": "SITE-003"}})

    # Check GET /api/v1/impact
    res_impact = auth_client.get("/api/v1/impact")
    assert res_impact.status_code == 200
    data = res_impact.json()

    assert "total_estimated_impact" in data
    assert "total_realized_savings" in data
    assert data["total_realized_savings"] > 0
    assert data["completed_actions_count"] >= 1
    assert "savings_by_action_type" in data
    assert "savings_by_site" in data
    assert "savings_by_equipment_type" in data
    assert len(data["recent_impact_records"]) >= 1


def test_action_impact_detail_endpoint(auth_client):
    res_action = auth_client.post(
        "/api/v1/actions",
        json={"equipment_id": "EQX1006", "action_type": "RETURN"},
    )
    action_id = res_action.json()["id"]

    # Before completion: realized_savings is 0
    res_detail_before = auth_client.get(f"/api/v1/actions/{action_id}/impact")
    assert res_detail_before.status_code == 200
    detail_before = res_detail_before.json()
    assert detail_before["avoided_cost"] > 0
    assert detail_before["realized_savings"] == 0.0

    # Complete action
    auth_client.post(f"/api/v1/actions/{action_id}/complete", json={})

    # After completion: realized_savings > 0
    res_detail_after = auth_client.get(f"/api/v1/actions/{action_id}/impact")
    assert res_detail_after.status_code == 200
    detail_after = res_detail_after.json()
    assert detail_after["realized_savings"] > 0
    assert "overdue" in detail_after["calculation_basis"].lower()
