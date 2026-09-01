import httpx
import json
from datetime import datetime, timedelta, timezone

api_client = httpx.Client(base_url="http://localhost:8000", timeout=10)
fe_client = httpx.Client(base_url="http://localhost:3000", timeout=10)

print("=== STARTING LIVE END-TO-END WORKFLOW TEST ===")

# Step 1: Check /scan endpoint on frontend
res_scan = fe_client.get("/scan")
assert res_scan.status_code == 200, f"GET /scan failed with status {res_scan.status_code}"
print("1. Frontend /scan page loaded: 200 OK")

# Step 2: Retrieve equipment EQX1007
res_eq = api_client.get("/api/v1/equipment/EQX1007")
assert res_eq.status_code == 200
eq_data = res_eq.json()
print(f"2. Identified EQX1007: initial_status={eq_data['status']}, current_rental={bool(eq_data.get('current_rental'))}")
assert eq_data["status"] == "UNASSIGNED", "EQX1007 should initially be UNASSIGNED"

# Step 3: Check Out EQX1007 to SITE-002 and OP-001
due_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
checkout_payload = {
    "equipment_id": "EQX1007",
    "site_id": "SITE-002",
    "operator_id": "OP-001",
    "due_at": due_date,
    "daily_rate": 420.0,
    "condition_notes": "Dispatched for Northside Logistics foundation",
    "actor": "Marcus Vance",
}

res_checkout = api_client.post("/api/v1/rentals/checkout", json=checkout_payload)
assert res_checkout.status_code == 201, f"Checkout failed: {res_checkout.status_code} {res_checkout.text}"
checkout_res = res_checkout.json()
print(f"3. Checkout Successful: success={checkout_res['success']}, status={checkout_res['status']}, rental_id={checkout_res['rental']['id']}")
assert checkout_res["status"] == "ACTIVE", f"Expected ACTIVE status, got {checkout_res['status']}"
assert checkout_res["rental"]["site"]["id"] == "SITE-002"
assert checkout_res["rental"]["operator"]["id"] == "OP-001"

# Step 4: Verify /assets/EQX1007 reflects the updated state
res_detail = api_client.get("/api/v1/equipment/EQX1007")
detail = res_detail.json()
print(f"4. Asset Detail EQX1007: status={detail['status']}, site={detail['site']['name']}, operator={detail['operator']['name']}")
assert detail["status"] == "ACTIVE"
assert detail["site"]["id"] == "SITE-002"
assert detail["operator"]["id"] == "OP-001"

# Step 5: Verify Dashboard KPIs updated
res_kpis = api_client.get("/api/v1/dashboard")
kpis = res_kpis.json()
print(f"5. Dashboard KPIs after checkout: active={kpis['active']}, unassigned={kpis['unassigned']}")
assert kpis["active"] == 3
assert kpis["unassigned"] == 1

# Step 6: Check In EQX1007
checkin_payload = {
    "equipment_id": "EQX1007",
    "condition": "Good",
    "notes": "Job complete, returned full tank to depot",
    "actor": "Elena Rostova",
}
res_checkin = api_client.post("/api/v1/rentals/checkin", json=checkin_payload)
assert res_checkin.status_code == 200, f"Checkin failed: {res_checkin.status_code} {res_checkin.text}"
checkin_res = res_checkin.json()
print(f"6. Checkin Successful: success={checkin_res['success']}, status={checkin_res['status']}, checked_in_at={checkin_res['rental']['checked_in_at']}")
assert checkin_res["status"] == "UNASSIGNED", f"Expected UNASSIGNED status, got {checkin_res['status']}"

# Step 7 & 8: Verify audit events contain CHECKOUT and CHECKIN
res_after = api_client.get("/api/v1/equipment/EQX1007")
after_data = res_after.json()
print(f"7. Equipment status after check-in: {after_data['status']}")
assert after_data["status"] == "UNASSIGNED"

audit_events = after_data.get("audit_timeline", [])
event_types = [ae["event_type"] for ae in audit_events]
print(f"8. Audit Timeline events for EQX1007: {event_types}")
assert "CHECKOUT" in event_types
assert "CHECKIN" in event_types

# Step 9: Verify Dashboard reflects final state
res_final_kpi = api_client.get("/api/v1/dashboard")
final_kpis = res_final_kpi.json()
print(f"9. Final Dashboard KPIs: active={final_kpis['active']}, unassigned={final_kpis['unassigned']}")
assert final_kpis["active"] == 2
assert final_kpis["unassigned"] == 2

print("\n=== ALL LIVE END-TO-END WORKFLOW VERIFICATIONS PASSED WITH 100% SUCCESS ===")
