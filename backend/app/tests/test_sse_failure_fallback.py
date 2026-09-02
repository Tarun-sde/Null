import os
import sys
import asyncio
import pytest

# Ensure backend root is on sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from main import app
from app.services.connection_manager import connection_manager

client = TestClient(app)


@pytest.mark.anyio
async def test_sse_failure_and_polling_recovery():
    print("=== TESTING SSE INTERRUPTION, POLLING FALLBACK, AND RECONNECTION ===")

    # 1. LIVE state: SSE subscriber queue registered
    queue = await connection_manager.connect()
    initial_subscribers = connection_manager.subscriber_count
    assert initial_subscribers >= 1
    print("1. [LIVE] SSE subscriber connected (Subscriber count >= 1)")

    try:
        # 2. Ingest telemetry while LIVE
        post_res = client.post("/api/v1/telemetry", json={
            "equipment_id": "EQX1005",
            "latitude": 37.8052,
            "longitude": -122.2708,
            "engine_hours": 50.0,
            "idle_hours": 3.0,
            "fuel_pct": 30.0,
        })
        assert post_res.status_code == 201

        # Verify event pushed to active subscriber queue
        event = await asyncio.wait_for(queue.get(), timeout=2.0)
        assert event["type"] == "telemetry"
        assert event["data"]["equipment_id"] == "EQX1005"
        assert event["data"]["engine_hours"] == 50.0
        print("2. [LIVE] Ingested telemetry for EQX1005, event received over SSE queue")
    finally:
        # 3. Simulate SSE Interruption (Disconnect client)
        connection_manager.disconnect(queue)

    assert connection_manager.subscriber_count == initial_subscribers - 1
    print("3. [INTERRUPTION] SSE connection interrupted and client disconnected")

    # 4. Ingest new telemetry during fallback period (SSE offline)
    post_res2 = client.post("/api/v1/telemetry", json={
        "equipment_id": "EQX1005",
        "latitude": 37.8055,
        "longitude": -122.2710,
        "engine_hours": 50.5,
        "idle_hours": 3.1,
        "fuel_pct": 29.5,
    })
    assert post_res2.status_code == 201
    print("4. [FALLBACK] Ingested new telemetry while SSE offline (DB engine_hours=50.5h)")

    # 5. POLLING state: Client polls equipment/dashboard API and receives latest telemetry
    poll_res = client.get("/api/v1/equipment/EQX1005")
    assert poll_res.status_code == 200
    eq_data = poll_res.json()
    assert eq_data["latest_telemetry"]["engine_hours"] == 50.5
    print("5. [POLLING] Fallback polling successfully fetched updated telemetry (50.5h)")

    # 6. RECOVERY / LIVE restored: Client reconnects SSE stream
    recovered_queue = await connection_manager.connect()
    assert connection_manager.subscriber_count == initial_subscribers
    print("6. [RECOVERY] SSE reconnected successfully (Status: LIVE restored)")

    try:
        # Ingest another event to verify recovered SSE stream receives events
        post_res3 = client.post("/api/v1/telemetry", json={
            "equipment_id": "EQX1005",
            "latitude": 37.8058,
            "longitude": -122.2712,
            "engine_hours": 51.0,
            "idle_hours": 3.2,
            "fuel_pct": 29.0,
        })
        assert post_res3.status_code == 201
        recovered_event = await asyncio.wait_for(recovered_queue.get(), timeout=2.0)
        assert recovered_event["data"]["engine_hours"] == 51.0
        print("7. [LIVE RESTORED] Recovered SSE stream verified receiving live telemetry events")
    finally:
        connection_manager.disconnect(recovered_queue)

    print("\n=== COMPLETE LIVE -> INTERRUPTION -> POLLING -> RECOVERY VERIFIED ===")


if __name__ == "__main__":
    asyncio.run(test_sse_failure_and_polling_recovery())



