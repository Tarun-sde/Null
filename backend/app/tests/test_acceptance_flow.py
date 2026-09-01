import httpx

def test_complete_acceptance_flow():
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=5.0) as client:
        # 1. Fetch recommendations
        recs = client.get("/api/v1/recommendations").json()
        assert len(recs) > 0
        rec = recs[0]
        rec_id = rec["id"]
        rec_eq = rec["equipment_id"]
        rec_type = rec["recommendation_type"]
        print(f"1. Selected Recommendation #{rec_id}: {rec_eq} -> {rec_type}")

        # 2. Trigger Action
        r_act = client.post(
            f"/api/v1/recommendations/{rec_id}/action",
            json={
                "notes": "Executing acceptance test reassignment",
                "actor": "Commander Marcus Vance",
                "payload": {"target_site_id": "SITE-003"},
            },
        )
        assert r_act.status_code == 201
        act = r_act.json()
        action_id = act["id"]
        status_val = act["status"]
        print(f"2. Action Created #{action_id} (Status: {status_val})")

        # 3. Complete Action
        r_comp = client.post(
            f"/api/v1/actions/{action_id}/complete",
            json={
                "notes": "Reassignment executed to Highland Medical Center",
                "actor": "Commander Marcus Vance",
                "payload": {"target_site_id": "SITE-003"},
            },
        )
        assert r_comp.status_code == 200
        comp = r_comp.json()
        assert comp["status"] == "COMPLETED"
        print(f"3. Action #{action_id} COMPLETED (completed_at: {comp['completed_at']})")

        # 4. Verify Invalid Transition Rejection (Cannot complete already completed action)
        r_dup = client.post(f"/api/v1/actions/{action_id}/complete", json={})
        assert r_dup.status_code == 400
        print("4. Invalid Transition Rejected: Cannot re-complete an already completed action (400 Bad Request)")

        # 5. Check Impact Ledger & Calculation Traceability
        imp = client.get(f"/api/v1/actions/{action_id}/impact").json()
        print(f"5. Realized Savings: ${imp['realized_savings']:.2f}")
        print(f"   Calculation Basis: {imp['calculation_basis']}")
        assert imp["realized_savings"] > 0
        assert imp["status"] == "COMPLETED"

        # 6. Fleet Impact Aggregation
        fleet_imp = client.get("/api/v1/impact").json()
        print(f"6. Total Fleet Realized ROI: ${fleet_imp['total_realized_savings']:.2f}")
        assert fleet_imp["total_realized_savings"] >= imp["realized_savings"]

        print("=== OPERATIONAL ACTION & FINANCIAL IMPACT FULLY VERIFIED ===")

if __name__ == "__main__":
    test_complete_acceptance_flow()
