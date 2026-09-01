import asyncio
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from main import app
from app.services.connection_manager import connection_manager

client = TestClient(app)


def test_ingest_telemetry_success():
    payload = {
        "equipment_id": "EQX1001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": 37.7750,
        "longitude": -122.4190,
        "engine_hours": 18.5,
        "idle_hours": 15.0,
        "fuel_pct": 79.5,
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["equipment_id"] == "EQX1001"
    assert data["latitude"] == 37.7750
    assert data["longitude"] == -122.4190
    assert data["engine_hours"] == 18.5
    assert data["idle_hours"] == 15.0
    assert data["fuel_pct"] == 79.5
    assert "id" in data


def test_ingest_telemetry_unknown_equipment():
    payload = {
        "equipment_id": "EQX9999",
        "latitude": 37.7750,
        "longitude": -122.4190,
        "engine_hours": 10.0,
        "idle_hours": 2.0,
        "fuel_pct": 80.0,
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_ingest_telemetry_invalid_latitude():
    payload = {
        "equipment_id": "EQX1001",
        "latitude": 95.0,  # Invalid > 90
        "longitude": -122.4190,
        "engine_hours": 10.0,
        "idle_hours": 2.0,
        "fuel_pct": 80.0,
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 422


def test_ingest_telemetry_invalid_longitude():
    payload = {
        "equipment_id": "EQX1001",
        "latitude": 37.7750,
        "longitude": -195.0,  # Invalid < -180
        "engine_hours": 10.0,
        "idle_hours": 2.0,
        "fuel_pct": 80.0,
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 422


def test_ingest_telemetry_invalid_runtime():
    # 1. Negative engine hours
    payload1 = {
        "equipment_id": "EQX1001",
        "latitude": 37.7750,
        "longitude": -122.4190,
        "engine_hours": -5.0,
        "idle_hours": 0.0,
        "fuel_pct": 80.0,
    }
    res1 = client.post("/api/v1/telemetry", json=payload1)
    assert res1.status_code == 422

    # 2. Idle hours exceeding engine hours
    payload2 = {
        "equipment_id": "EQX1001",
        "latitude": 37.7750,
        "longitude": -122.4190,
        "engine_hours": 10.0,
        "idle_hours": 15.0,  # Invalid: idle > engine
        "fuel_pct": 80.0,
    }
    res2 = client.post("/api/v1/telemetry", json=payload2)
    assert res2.status_code == 422


def test_ingest_telemetry_invalid_fuel():
    payload = {
        "equipment_id": "EQX1001",
        "latitude": 37.7750,
        "longitude": -122.4190,
        "engine_hours": 10.0,
        "idle_hours": 2.0,
        "fuel_pct": 110.0,  # Invalid > 100
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 422


def test_get_latest_telemetry_success():
    response = client.get("/api/v1/equipment/EQX1001/telemetry/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["equipment_id"] == "EQX1001"
    assert "latitude" in data
    assert "longitude" in data
    assert "engine_hours" in data


def test_get_latest_telemetry_unknown_equipment():
    response = client.get("/api/v1/equipment/EQX9999/telemetry/latest")
    assert response.status_code == 404


def test_get_telemetry_history_success():
    response = client.get("/api/v1/equipment/EQX1001/telemetry?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["equipment_id"] == "EQX1001"


def test_get_telemetry_history_unknown_equipment():
    response = client.get("/api/v1/equipment/EQX9999/telemetry")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_connection_manager_broadcast_and_disconnect():
    queue = await connection_manager.connect()
    initial_count = connection_manager.subscriber_count
    assert initial_count >= 1

    # Broadcast test event
    test_data = {"equipment_id": "EQX1001", "status": "ACTIVE"}
    await connection_manager.broadcast("telemetry", test_data)

    event = await asyncio.wait_for(queue.get(), timeout=2.0)
    assert event["type"] == "telemetry"
    assert event["data"]["equipment_id"] == "EQX1001"

    # Disconnect
    connection_manager.disconnect(queue)
    assert connection_manager.subscriber_count == initial_count - 1
