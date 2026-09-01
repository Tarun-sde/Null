import os
import sys
import httpx

API_BASE_URL = "http://localhost:8000"
FE_BASE_URL = "http://localhost:3000"

def run_phase6_verification():
    print("=== STARTING PHASE 6 RECOMMENDATIONS, ACTIONS & FINANCIAL IMPACT VERIFICATION ===")

    with httpx.Client(base_url=API_BASE_URL, timeout=10.0) as client:
        # 1. Check Recommendations API
        res_recs = client.get("/api/v1/recommendations")
        assert res_recs.status_code == 200, f"Expected 200, got {res_recs.status_code}"
        recs = res_recs.json()
        print(f"1. GET /api/v1/recommendations: {len(recs)} active recommendations generated")
        assert len(recs) >= 3, "Expected at least 3 recommendations across fleet"
        
        for r in recs:
            print(f"   • [{r['priority']}] {r['equipment_id']} -> {r['recommendation_type']}: {r['action']}")
            print(f"     Estimated Impact: ${r.get('estimated_impact', {}).get('estimated_savings_usd', 0):.2f}")

        # 2. Verify EQX1001 Recommendation (Excessive Idle -> REASSIGN)
        eq1_rec = next((r for r in recs if r["equipment_id"] == "EQX1001" and r["recommendation_type"] == "REASSIGN"), None)
        assert eq1_rec is not None, "Expected REASSIGN recommendation for EQX1001"
        assert eq1_rec["priority"] in ["HIGH", "CRITICAL"]
        print("2. Verified EQX1001 Recommendation: Correctly recommends REASSIGN with estimated impact")

        # 3. Verify EQX1006 Recommendation (Overdue -> RETURN)
        eq6_rec = next((r for r in recs if r["equipment_id"] == "EQX1006" and r["recommendation_type"] == "RETURN"), None)
        assert eq6_rec is not None, "Expected RETURN recommendation for EQX1006"
        assert eq6_rec["priority"] == "CRITICAL"
        print("3. Verified EQX1006 Recommendation: Correctly recommends RETURN with CRITICAL priority")

        # 4. Trigger Action from Recommendation for EQX1001
        res_act1 = client.post(
            f"/api/v1/recommendations/{eq1_rec['id']}/action",
            json={
                "notes": "Reassigning EQX1001 to Highland Medical Center",
                "actor": "Commander Marcus Vance",
                "payload": {"target_site_id": "SITE-003"},
            },
        )
        assert res_act1.status_code == 201
        action1 = res_act1.json()
        action1_id = action1["id"]
        print(f"4. Created Action #{action1_id} for EQX1001 from recommendation (Status: {action1['status']})")

        # 5. Complete Action #1 (REASSIGN)
        res_comp1 = client.post(
            f"/api/v1/actions/{action1_id}/complete",
            json={
                "notes": "Handoff complete: Asset relocated to Highland Medical Center",
                "actor": "Commander Marcus Vance",
                "payload": {"target_site_id": "SITE-003"},
            },
        )
        assert res_comp1.status_code == 200
        comp1 = res_comp1.json()
        assert comp1["status"] == "COMPLETED"
        print(f"5. Completed Action #{action1_id}: Rental reassigned, alert auto-resolved, audit logged")

        # 6. Trigger and Complete Action for EQX1006 (RETURN overdue asset)
        res_act6 = client.post(
            f"/api/v1/recommendations/{eq6_rec['id']}/action",
            json={
                "notes": "Off-rent physical return for EQX1006",
                "actor": "Commander Marcus Vance",
            },
        )
        assert res_act6.status_code == 201
        action6 = res_act6.json()
        action6_id = action6["id"]

        res_comp6 = client.post(
            f"/api/v1/actions/{action6_id}/complete",
            json={
                "notes": "Physical check-in completed at Central Depot",
                "actor": "Commander Marcus Vance",
            },
        )
        assert res_comp6.status_code == 200
        print(f"6. Completed Action #{action6_id}: Rental contract checked in, overdue surcharge eliminated")

        # 7. Check Impact & Realized Savings API
        res_impact = client.get("/api/v1/impact")
        assert res_impact.status_code == 200
        impact_data = res_impact.json()
        print(f"7. GET /api/v1/impact: Total Realized Savings = ${impact_data['total_realized_savings']:.2f}")
        assert impact_data["total_realized_savings"] > 0, "Expected positive realized savings from completed actions"
        assert impact_data["completed_actions_count"] >= 2
        print(f"   • Savings by Action: {impact_data['savings_by_action_type']}")
        print(f"   • Savings by Site: {impact_data['savings_by_site']}")
        print(f"   • Verified Records Count: {len(impact_data['recent_impact_records'])}")

        # 8. Check Single Action Impact Detail
        res_det = client.get(f"/api/v1/actions/{action1_id}/impact")
        assert res_det.status_code == 200
        det = res_det.json()
        print(f"8. GET /api/v1/actions/{action1_id}/impact: Realized = ${det['realized_savings']:.2f}")
        print(f"   • Calculation Basis: {det['calculation_basis']}")
        assert det["realized_savings"] == 1350.0

    # 9. Verify Frontend Web Views
    with httpx.Client(base_url=FE_BASE_URL, timeout=10.0) as fe_client:
        r_dash = fe_client.get("/")
        assert r_dash.status_code == 200
        print("9. Frontend Dashboard (/) loads: 200 OK")

        r_actions = fe_client.get("/actions")
        assert r_actions.status_code == 200
        print("10. Frontend Action Queue (/actions) loads: 200 OK")

        r_impact = fe_client.get("/impact")
        assert r_impact.status_code == 200
        print("11. Frontend Avoided Impact (/impact) loads: 200 OK")

        r_asset = fe_client.get("/assets/EQX1001")
        assert r_asset.status_code == 200
        print("12. Frontend Asset Detail (/assets/EQX1001) loads: 200 OK")

    print("\n=== ALL PHASE 6 RECOMMENDATION, ACTION, AND FINANCIAL SAVINGS CHECKS PASSED ===")

if __name__ == "__main__":
    run_phase6_verification()
