import os
import sys
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal
from app.models import Equipment, Rental, Telemetry, Recommendation
from app.analytics.recommendation_engine import (
    evaluate_equipment_recommendations,
    generate_fleet_recommendations,
    calculate_idle_reassignment_impact,
    calculate_overdue_return_impact,
)
from app.seed.seed import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    db = SessionLocal()
    seed_database(db, reset=True)
    yield
    db.close()


def test_calculate_idle_reassignment_impact():
    impact = calculate_idle_reassignment_impact(daily_rate=18500.0, idle_hours=14.2)
    assert impact["impact_type"] == "IDLE_AVOIDANCE"
    assert impact["daily_rate"] == 18500.0
    assert impact["avoidable_days"] == 1.8
    assert impact["estimated_savings_usd"] == 33300.0
    assert "1.8 avoidable idle days" in impact["calculation_basis"]


def test_calculate_overdue_return_impact():
    impact = calculate_overdue_return_impact(daily_rate=7500.0, overdue_hours=48.0)
    assert impact["impact_type"] == "OVERDUE_SURCHARGE_AVOIDED"
    assert impact["daily_rate"] == 7500.0
    assert impact["days_overdue"] == 2.0
    assert impact["estimated_savings_usd"] == 15000.0
    assert "2.0 overdue days" in impact["calculation_basis"]


def test_excessive_idle_generates_reassign_recommendation():
    db = SessionLocal()
    eq1 = db.query(Equipment).filter(Equipment.id == "EQX1001").first()
    recs = evaluate_equipment_recommendations(eq1)
    
    assert len(recs) >= 1
    reassign_rec = next((r for r in recs if r.recommendation_type == "REASSIGN"), None)
    assert reassign_rec is not None
    assert reassign_rec.priority in ["HIGH", "CRITICAL"]
    assert "reassign" in reassign_rec.explanation.lower()
    assert reassign_rec.estimated_impact["estimated_savings_usd"] > 0
    assert reassign_rec.target_site_id is not None
    db.close()


def test_overdue_equipment_generates_return_recommendation():
    db = SessionLocal()
    eq6 = db.query(Equipment).filter(Equipment.id == "EQX1006").first()
    recs = evaluate_equipment_recommendations(eq6)

    return_rec = next((r for r in recs if r.recommendation_type == "RETURN"), None)
    assert return_rec is not None
    assert return_rec.priority == "CRITICAL"
    assert "overdue" in return_rec.explanation.lower()
    assert return_rec.estimated_impact["impact_type"] == "OVERDUE_SURCHARGE_AVOIDED"
    db.close()


def test_missing_assignment_generates_investigate_recommendation():
    db = SessionLocal()
    eq2 = db.query(Equipment).filter(Equipment.id == "EQX1002").first()
    recs = evaluate_equipment_recommendations(eq2)

    inv_rec = next((r for r in recs if r.recommendation_type == "INVESTIGATE"), None)
    assert inv_rec is not None
    assert inv_rec.priority == "HIGH"
    assert "operator" in inv_rec.explanation.lower()
    db.close()


def test_healthy_equipment_generates_no_critical_recommendations():
    db = SessionLocal()
    eq5 = db.query(Equipment).filter(Equipment.id == "EQX1005").first()
    recs = evaluate_equipment_recommendations(eq5)
    assert len(recs) == 0
    db.close()


def test_fleet_recommendations_endpoint():
    response = client.get("/api/v1/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # Check structure
    rec = data[0]
    assert "id" in rec
    assert "equipment_id" in rec
    assert "recommendation_type" in rec
    assert "priority" in rec
    assert "explanation" in rec
    assert "action" in rec
    assert "confidence" in rec
    assert "status" in rec


def test_recommendations_filter_by_equipment_and_priority():
    response = client.get("/api/v1/recommendations?equipment_id=EQX1001&priority=HIGH")
    assert response.status_code == 200
    data = response.json()
    for r in data:
        assert r["equipment_id"] == "EQX1001"
        assert r["priority"] == "HIGH"


def test_trigger_action_from_recommendation(auth_client):
    # First get list
    res_list = auth_client.get("/api/v1/recommendations")
    assert res_list.status_code == 200
    recs = res_list.json()
    assert len(recs) > 0
    rec_id = recs[0]["id"]

    # Trigger action
    res_action = auth_client.post(
        f"/api/v1/recommendations/{rec_id}/action",
        json={
            "notes": "Initiated operational review from recommendations panel",
            "actor": "Commander Marcus Vance",
        },
    )
    assert res_action.status_code == 201
    action_data = res_action.json()
    assert action_data["recommendation_id"] == rec_id
    assert action_data["status"] == "PENDING"
    assert action_data["actor"] == "Commander Marcus Vance"
