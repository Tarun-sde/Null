import sys
import time
import asyncio
import httpx
from datetime import datetime, timezone

API_BASE_URL = "http://localhost:8000"
FE_BASE_URL = "http://localhost:3000"

async def test_live_stream_and_simulator():
    print("=== STARTING PHASE 4 REALTIME & SSE E2E VERIFICATION ===")

    # 1. Check initial telemetry count in DB
    client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0)
    res_init = await client.get("/api/v1/equipment/EQX1001/telemetry?limit=500")
    assert res_init.status_code == 200
    initial_count = len(res_init.json())
    print(f"1. Initial telemetry count for EQX1001: {initial_count}")

    # 2. Open SSE stream connection
    received_events = []
    sse_connected_event = asyncio.Event()

    async def sse_listener():
        async with httpx.AsyncClient(timeout=30.0) as stream_client:
            async with stream_client.stream("GET", f"{API_BASE_URL}/api/v1/telemetry/stream") as response:
                assert response.status_code == 200
                sse_connected_event.set()
                print("2. SSE Client successfully connected to /api/v1/telemetry/stream (Status: LIVE)")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        event_data = line[6:]
                        received_events.append(event_data)
                        if len(received_events) >= 7:
                            break

    listener_task = asyncio.create_task(sse_listener())
    await asyncio.wait_for(sse_connected_event.wait(), timeout=5.0)

    # 3. Ingest simulated telemetry for seeded equipment
    now = datetime.now(timezone.utc)
    for eq_id in ["EQX1001", "EQX1002", "EQX1003", "EQX1004", "EQX1005", "EQX1006", "EQX1007"]:
        payload = {
            "equipment_id": eq_id,
            "timestamp": now.isoformat(),
            "latitude": 37.7750,
            "longitude": -122.4190,
            "engine_hours": 20.0,
            "idle_hours": 5.0,
            "fuel_pct": 80.0,
        }
        res_post = await client.post("/api/v1/telemetry", json=payload)
        assert res_post.status_code == 201

    # 4. Wait for SSE listener to collect all 7 live events
    await asyncio.wait_for(listener_task, timeout=5.0)
    print(f"3. SSE Stream broadcast received {len(received_events)} live telemetry events in real time!")
    assert len(received_events) >= 7

    # 5. Verify database row increment
    res_after = await client.get("/api/v1/equipment/EQX1001/telemetry?limit=500")
    new_count = len(res_after.json())
    print(f"4. Updated telemetry count for EQX1001: {new_count} (Rows increased: {new_count > initial_count})")
    assert new_count > initial_count

    # 6. Verify latest telemetry endpoint
    res_latest = await client.get("/api/v1/equipment/EQX1001/telemetry/latest")
    assert res_latest.status_code == 200
    latest_data = res_latest.json()
    print(f"5. Latest telemetry retrieved: engine_hours={latest_data['engine_hours']}, fuel={latest_data['fuel_pct']}%")
    assert latest_data["engine_hours"] == 20.0

    # 7. Verify frontend dashboard & asset detail routes load
    async with httpx.AsyncClient(base_url=FE_BASE_URL, timeout=10.0) as fe_client:
        r_home = await fe_client.get("/")
        assert r_home.status_code == 200
        print("6. Frontend dashboard page loaded: 200 OK")

        r_asset = await fe_client.get("/assets/EQX1005")
        assert r_asset.status_code == 200
        print("7. Frontend /assets/EQX1005 page loaded: 200 OK")

    await client.aclose()
    print("\n=== ALL REALTIME SSE AND INGESTION VERIFICATIONS PASSED ===")

if __name__ == "__main__":
    asyncio.run(test_live_stream_and_simulator())
