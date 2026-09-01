import os
import sys
import httpx
from datetime import datetime, timezone

API_BASE_URL = "http://localhost:8000"
FE_BASE_URL = "http://localhost:3000"


def verify_production_deployment():
    print("=== STARTING PHASE 7 PRODUCTION HARDENING & SMOKE TEST VERIFICATION ===")

    with httpx.Client(base_url=API_BASE_URL, timeout=10.0) as client:
        # 1. Health & Readiness Probes
        r_health = client.get("/health")
        assert r_health.status_code == 200, f"Health check failed: {r_health.status_code}"
        health_data = r_health.json()
        assert health_data["status"] == "healthy"
        print(f"1. Health Check (/health): {health_data}")

        r_ready = client.get("/ready")
        assert r_ready.status_code == 200, f"Readiness check failed: {r_ready.status_code}"
        ready_data = r_ready.json()
        assert ready_data["status"] == "ready" and ready_data["database"] == "connected"
        print(f"2. Readiness Check (/ready): {ready_data}")

        # 2. CORS Verification
        r_cors = client.options(
            "/api/v1/equipment",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r_cors.status_code == 200
        assert r_cors.headers.get("access-control-allow-origin") == "http://localhost:3000"
        print("3. CORS Security: Origin correctly validated and headers enforced")

        # 3. Core API Endpoints Smoke Test
        endpoints = [
            "/api/v1/dashboard",
            "/api/v1/equipment",
            "/api/v1/equipment/EQX1001",
            "/api/v1/anomalies",
            "/api/v1/alerts",
            "/api/v1/forecasts",
            "/api/v1/forecasts/summary",
            "/api/v1/recommendations",
            "/api/v1/actions",
            "/api/v1/impact",
            "/api/v1/sites",
            "/api/v1/operators",
        ]
        for ep in endpoints:
            res = client.get(ep)
            assert res.status_code == 200, f"Endpoint {ep} returned {res.status_code}"
        print(f"4. Core APIs: All {len(endpoints)} endpoints returned 200 OK")

        # 4. Input Validation & Error Handling
        r_invalid = client.post(
            "/api/v1/telemetry",
            json={"equipment_id": "EQX1001", "latitude": 999, "longitude": -74, "engine_hours": 10, "idle_hours": 2, "fuel_pct": -10},
        )
        assert r_invalid.status_code == 422
        assert r_invalid.json()["status"] == "error"
        assert r_invalid.json()["error_code"] == "VALIDATION_ERROR"
        print("5. Input Validation: 422 Unprocessable Entity with sanitized error response")

        # 5. Full Business Flow: Recommend -> Action -> Complete -> Realized ROI
        r_recs = client.get("/api/v1/recommendations")
        recs = r_recs.json()
        assert len(recs) > 0
        target_rec = recs[0]

        # Trigger Action
        r_act = client.post(
            f"/api/v1/recommendations/{target_rec['id']}/action",
            json={
                "notes": f"Executing production hardened action: {target_rec['action']}",
                "actor": "Commander Marcus Vance",
                "payload": target_rec.get("estimated_impact", {}),
            },
        )
        assert r_act.status_code == 201
        act = r_act.json()
        action_id = act["id"]

        # Complete Action
        r_comp = client.post(
            f"/api/v1/actions/{action_id}/complete",
            json={
                "notes": "Verified resolution on site",
                "actor": "Commander Marcus Vance",
                "payload": {"target_site_id": "SITE-003"},
            },
        )
        assert r_comp.status_code == 200
        assert r_comp.json()["status"] == "COMPLETED"

        # Verify Realized Impact
        r_impact = client.get("/api/v1/impact")
        impact = r_impact.json()
        assert impact["total_realized_savings"] > 0
        print(f"6. Full Business Flow: Action #{action_id} completed, Realized ROI = ${impact['total_realized_savings']:.2f}")

    # 6. Frontend Route Smoke Tests
    with httpx.Client(base_url=FE_BASE_URL, timeout=10.0) as fe_client:
        fe_routes = [
            "/",
            "/dashboard",
            "/assets",
            "/assets/EQX1001",
            "/scan",
            "/forecast",
            "/actions",
            "/impact",
        ]
        for route in fe_routes:
            r = fe_client.get(route)
            assert r.status_code == 200, f"Frontend route {route} returned {r.status_code}"
        print(f"7. Frontend Web Routes: All {len(fe_routes)} production routes rendered 200 OK")

    print("\n=== ALL PHASE 7 PRODUCTION HARDENING & SMOKE TESTS PASSED SUCCESSFULLY ===")


if __name__ == "__main__":
    verify_production_deployment()
