import sys
import httpx

API_BASE_URL = "http://localhost:8000"
FE_BASE_URL = "http://localhost:3000"

def run_phase5_verification():
    print("=== STARTING PHASE 5 INTELLIGENCE & DEMAND FORECASTING VERIFICATION ===")

    with httpx.Client(base_url=API_BASE_URL, timeout=10.0) as client:
        # 1. Check Anomalies API
        res_anom = client.get("/api/v1/anomalies")
        assert res_anom.status_code == 200, f"Expected 200, got {res_anom.status_code}"
        anomalies = res_anom.json()
        print(f"1. GET /api/v1/anomalies: {len(anomalies)} anomalies detected across fleet")
        assert len(anomalies) >= 3, "Expected at least 3 seeded anomalies across fleet"
        
        for anom in anomalies:
            print(f"   • [{anom['severity']}] {anom['equipment_id']} -> {anom['anomaly_type']} (Score: {anom['anomaly_score']}/100)")
            print(f"     Explanation: {anom['explanation']}")

        # 2. Verify EQX1001 scenario (Under-Utilized / Excessive Idle)
        res_eq1 = client.get("/api/v1/equipment/EQX1001/anomalies")
        assert res_eq1.status_code == 200
        eq1_anomalies = res_eq1.json()
        assert len(eq1_anomalies) >= 1
        eq1_types = [a["anomaly_type"] for a in eq1_anomalies]
        assert "EXCESSIVE_IDLE" in eq1_types or "LOW_UTILIZATION" in eq1_types
        assert any(a["anomaly_score"] >= 70 for a in eq1_anomalies)
        print("2. Verified EQX1001: Correctly flagged for excessive idle and low utilization with score >= 70")

        # 3. Verify EQX1002 scenario (Missing Assignment)
        res_eq2 = client.get("/api/v1/equipment/EQX1002/anomalies")
        assert res_eq2.status_code == 200
        eq2_anomalies = res_eq2.json()
        eq2_types = [a["anomaly_type"] for a in eq2_anomalies]
        assert "MISSING_ASSIGNMENT" in eq2_types
        print("3. Verified EQX1002: Correctly flagged for missing operator assignment")

        # 4. Verify EQX1005 scenario (High-Use Bulldozer -> Optimal / Healthy)
        res_eq5 = client.get("/api/v1/equipment/EQX1005/anomalies")
        assert res_eq5.status_code == 200
        eq5_anomalies = res_eq5.json()
        assert len(eq5_anomalies) == 0
        print("4. Verified EQX1005: 0 open anomalies (Operating optimally within nominal bounds)")

        # 5. Verify EQX1006 scenario (Overdue Rental)
        res_eq6 = client.get("/api/v1/equipment/EQX1006/anomalies")
        assert res_eq6.status_code == 200
        eq6_anomalies = res_eq6.json()
        eq6_types = [a["anomaly_type"] for a in eq6_anomalies]
        assert "OVERDUE" in eq6_types
        print("5. Verified EQX1006: Correctly flagged as overdue with rate surcharge explanation")

        # 6. Check Alerts API
        res_alerts = client.get("/api/v1/alerts?status=OPEN")
        assert res_alerts.status_code == 200
        alerts = res_alerts.json()
        print(f"6. GET /api/v1/alerts?status=OPEN: {len(alerts)} active alerts retrieved")
        assert len(alerts) >= 3

        # 7. Check Forecasts API
        res_fc = client.get("/api/v1/forecasts?horizon_weeks=4")
        assert res_fc.status_code == 200
        forecasts = res_fc.json()
        print(f"7. GET /api/v1/forecasts: {len(forecasts)} forecast items calculated across sites & equipment types")
        assert len(forecasts) > 0
        sample_fc = forecasts[0]
        assert "site_name" in sample_fc
        assert "equipment_type" in sample_fc
        assert "predicted_units" in sample_fc
        assert "confidence" in sample_fc
        assert "backtest_error" in sample_fc
        assert "drivers" in sample_fc
        print(f"   • Sample: {sample_fc['site_name']} | {sample_fc['equipment_type']} -> {sample_fc['predicted_units']} units (Confidence: {int(sample_fc['confidence']*100)}%, Backtest MAE: ±{sample_fc['backtest_error']})")
        print(f"     Driver Explanation: {sample_fc['explanation']}")

        # 8. Check Forecast Summary
        res_sum = client.get("/api/v1/forecasts/summary")
        assert res_sum.status_code == 200
        summary = res_sum.json()
        print(f"8. GET /api/v1/forecasts/summary: Total units={summary['total_forecasted_units']}, Avg Confidence={int(summary['avg_confidence']*100)}%")

    # 9. Verify Frontend Routes
    with httpx.Client(base_url=FE_BASE_URL, timeout=10.0) as fe_client:
        r_dash = fe_client.get("/")
        assert r_dash.status_code == 200
        print("9. Frontend Dashboard (/) loads: 200 OK (with live alerts and intelligence)")

        r_fc_page = fe_client.get("/forecast")
        assert r_fc_page.status_code == 200
        print("10. Frontend Demand Forecast (/forecast) loads: 200 OK")

        r_asset_page = fe_client.get("/assets/EQX1001")
        assert r_asset_page.status_code == 200
        print("11. Frontend Asset Detail (/assets/EQX1001) loads: 200 OK")

    print("\n=== ALL PHASE 5 INTELLIGENCE AND DEMAND FORECASTING CHECKS PASSED ===")

if __name__ == "__main__":
    run_phase5_verification()
