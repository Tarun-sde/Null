import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_cors_headers_allowed_origin():
    response = client.options(
        "/api/v1/equipment",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_headers_disallowed_origin():
    response = client.options(
        "/api/v1/equipment",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Origin is not allowed
    assert response.headers.get("access-control-allow-origin") != "http://malicious-site.com"


def test_invalid_telemetry_payload_validation_error():
    # Negative fuel_pct and invalid latitude
    response = client.post(
        "/api/v1/telemetry",
        json={
            "equipment_id": "EQX1001",
            "latitude": 999.0,
            "longitude": -74.006,
            "engine_hours": 10.0,
            "idle_hours": 2.0,
            "fuel_pct": -5.0,
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["error_code"] == "VALIDATION_ERROR"


def test_invalid_pagination_bounds():
    response = client.get("/api/v1/alerts?limit=9999")
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"


def test_not_found_clean_error_response():
    response = client.get("/api/v1/equipment/NONEXISTENT_ASSET")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["error_code"] == "HTTP_404"
    assert "not found" in data["message"].lower()
