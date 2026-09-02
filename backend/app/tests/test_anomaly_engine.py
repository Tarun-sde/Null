import pytest
from datetime import datetime, timedelta, timezone
from app.models import Equipment, Rental, Telemetry, Site, Operator, Alert
from app.analytics.anomaly_engine import (
    evaluate_excessive_idle,
    evaluate_zero_runtime,
    evaluate_missing_assignment,
    evaluate_overdue_rental,
    evaluate_low_utilization,
    evaluate_equipment_anomalies,
    map_score_to_severity,
)
from app.services.alert_service import sync_equipment_alerts
from app.db.session import SessionLocal

ANCHOR_TIME = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_map_score_to_severity():
    assert map_score_to_severity(85) == "CRITICAL"
    assert map_score_to_severity(70) == "CRITICAL"
    assert map_score_to_severity(69) == "WARNING"
    assert map_score_to_severity(40) == "WARNING"
    assert map_score_to_severity(39) == "INFO"
    assert map_score_to_severity(0) == "INFO"


def test_rule_excessive_idle():
    tel = Telemetry(equipment_id="EQX1001", engine_hours=16.0, idle_hours=14.2)
    res = evaluate_excessive_idle("EQX1001", telemetry=tel, rental=None, now=ANCHOR_TIME)
    
    assert res is not None
    assert res.anomaly_type == "EXCESSIVE_IDLE"
    assert res.anomaly_score >= 70
    assert res.severity == "CRITICAL"
    assert "14.2" in res.explanation
    assert "8.0" in res.explanation
    assert res.supporting_signals["idle_hours"] == 14.2
    assert res.supporting_signals["threshold_hours"] == 8.0


def test_rule_excessive_idle_healthy():
    tel = Telemetry(equipment_id="EQX1003", engine_hours=28.5, idle_hours=4.0)
    res = evaluate_excessive_idle("EQX1003", telemetry=tel, rental=None, now=ANCHOR_TIME)
    assert res is None


def test_rule_zero_runtime():
    rental = Rental(id=10, equipment_id="EQX1007", checked_out_at=ANCHOR_TIME - timedelta(days=2), checked_in_at=None)
    tel = Telemetry(equipment_id="EQX1007", engine_hours=0.0, idle_hours=0.0)
    res = evaluate_zero_runtime("EQX1007", telemetry=tel, rental=rental, now=ANCHOR_TIME)
    
    assert res is not None
    assert res.anomaly_type == "ZERO_RUNTIME"
    assert res.anomaly_score == 55
    assert res.severity == "WARNING"
    assert "0.0h" in res.explanation


def test_rule_missing_operator_assignment():
    rental = Rental(id=11, equipment_id="EQX1002", site_id="SITE-002", operator_id=None, checked_in_at=None)
    res = evaluate_missing_assignment("EQX1002", rental=rental, now=ANCHOR_TIME)
    
    assert res is not None
    assert res.anomaly_type == "MISSING_ASSIGNMENT"
    assert res.severity == "WARNING"
    assert "operator" in res.explanation
    assert "operator" in res.supporting_signals["missing_fields"]


def test_rule_missing_site_assignment():
    rental = Rental(id=12, equipment_id="EQX1002", site_id=None, operator_id="OP-001", checked_in_at=None)
    res = evaluate_missing_assignment("EQX1002", rental=rental, now=ANCHOR_TIME)
    
    assert res is not None
    assert res.anomaly_type == "MISSING_ASSIGNMENT"
    assert "site" in res.explanation


def test_rule_overdue_rental():
    due_at = ANCHOR_TIME - timedelta(hours=48)
    rental = Rental(
        id=13,
        equipment_id="EQX1006",
        checked_out_at=ANCHOR_TIME - timedelta(days=10),
        due_at=due_at,
        checked_in_at=None,
        daily_rate=7500.0,
    )
    res = evaluate_overdue_rental("EQX1006", rental=rental, daily_rate=7500.0, now=ANCHOR_TIME)
    
    assert res is not None
    assert res.anomaly_type == "OVERDUE"
    assert res.anomaly_score >= 80
    assert res.severity == "CRITICAL"
    assert "48.0h overdue" in res.explanation
    assert "₹7,500.00" in res.explanation
    assert res.supporting_signals["overdue_hours"] == 48.0


def test_rule_low_utilization():
    tel = Telemetry(equipment_id="EQX1001", engine_hours=16.0, idle_hours=14.2)
    rental = Rental(id=1, equipment_id="EQX1001", checked_in_at=None)
    res = evaluate_low_utilization("EQX1001", telemetry=tel, rental=rental, now=ANCHOR_TIME)
    
    assert res is not None
    assert res.anomaly_type == "LOW_UTILIZATION"
    assert res.severity in ["WARNING", "CRITICAL"]
    assert "11.2%" in res.explanation
    assert "20%" in res.explanation
    assert res.supporting_signals["utilization_rate"] == 0.1125


def test_healthy_equipment_no_anomalies():
    eq = Equipment(id="EQX1003", type="Wheel Loader", daily_rate=380.0)
    rental = Rental(
        id=3,
        equipment_id="EQX1003",
        site_id="SITE-001",
        operator_id="OP-002",
        checked_out_at=ANCHOR_TIME - timedelta(days=4),
        due_at=ANCHOR_TIME + timedelta(days=5),
        checked_in_at=None,
    )
    tel = Telemetry(equipment_id="EQX1003", engine_hours=28.5, idle_hours=4.2)
    
    anomalies = evaluate_equipment_anomalies(
        equipment=eq,
        rental=rental,
        latest_telemetry=tel,
        now=ANCHOR_TIME,
    )
    assert len(anomalies) == 0


def test_multi_signal_compound_scoring():
    eq = Equipment(id="EQX1001", type="Excavator", daily_rate=450.0)
    rental = Rental(
        id=1,
        equipment_id="EQX1001",
        site_id="SITE-001",
        operator_id="OP-001",
        checked_out_at=ANCHOR_TIME - timedelta(days=5),
        due_at=ANCHOR_TIME + timedelta(days=10),
        checked_in_at=None,
    )
    tel = Telemetry(equipment_id="EQX1001", engine_hours=16.0, idle_hours=14.2)
    
    # EQX1001 triggers both EXCESSIVE_IDLE and LOW_UTILIZATION
    anomalies = evaluate_equipment_anomalies(
        equipment=eq,
        rental=rental,
        latest_telemetry=tel,
        now=ANCHOR_TIME,
    )
    assert len(anomalies) == 2
    types = [a.anomaly_type for a in anomalies]
    assert "EXCESSIVE_IDLE" in types
    assert "LOW_UTILIZATION" in types
    # Top anomaly score has multi-signal boost applied
    assert anomalies[0].anomaly_score >= 80


def test_score_and_explanation_determinism():
    tel = Telemetry(equipment_id="EQX1001", engine_hours=16.0, idle_hours=14.2)
    rental = Rental(id=1, equipment_id="EQX1001", checked_in_at=None)
    
    res1 = evaluate_excessive_idle("EQX1001", telemetry=tel, rental=rental, now=ANCHOR_TIME)
    res2 = evaluate_excessive_idle("EQX1001", telemetry=tel, rental=rental, now=ANCHOR_TIME)
    
    assert res1.anomaly_score == res2.anomaly_score
    assert res1.explanation == res2.explanation
    assert res1.severity == res2.severity


def test_alert_deduplication_and_resolution():
    db = SessionLocal()
    try:
        # 1. Clean and setup test equipment
        db.query(Alert).filter(Alert.equipment_id == "TEST-EQ-001").delete()
        test_eq = db.query(Equipment).filter(Equipment.id == "TEST-EQ-001").first()
        if not test_eq:
            db.add(Equipment(id="TEST-EQ-001", type="Excavator", dealer="Test Dealer", daily_rate=500.0))
        db.commit()

        # 2. Simulate first anomaly cycle -> creates 1 alert
        tel = Telemetry(equipment_id="TEST-EQ-001", engine_hours=16.0, idle_hours=14.2)
        rental = Rental(id=99, equipment_id="TEST-EQ-001", site_id="SITE-001", operator_id="OP-001", checked_in_at=None)
        eq = Equipment(id="TEST-EQ-001", type="Excavator", daily_rate=500.0)

        anomalies_1 = evaluate_equipment_anomalies(eq, rental=rental, latest_telemetry=tel, now=ANCHOR_TIME)
        alerts_1 = sync_equipment_alerts(db, "TEST-EQ-001", anomalies_1, now=ANCHOR_TIME)
        assert len(alerts_1) == 2
        initial_ids = [a.id for a in alerts_1]

        # 3. Simulate second telemetry cycle with ongoing anomaly -> deduplicates (updates existing, does not duplicate IDs)
        tel_2 = Telemetry(equipment_id="TEST-EQ-001", engine_hours=16.5, idle_hours=14.7)
        anomalies_2 = evaluate_equipment_anomalies(eq, rental=rental, latest_telemetry=tel_2, now=ANCHOR_TIME + timedelta(minutes=5))
        alerts_2 = sync_equipment_alerts(db, "TEST-EQ-001", anomalies_2, now=ANCHOR_TIME + timedelta(minutes=5))
        second_ids = [a.id for a in alerts_2]
        
        # Verify IDs match (no duplicate rows created)
        assert initial_ids == second_ids
        total_open = db.query(Alert).filter(Alert.equipment_id == "TEST-EQ-001", Alert.status == "OPEN").count()
        assert total_open == 2

        # 4. Simulate condition cleared (e.g. equipment returned / healthy) -> auto-resolves open alerts
        alerts_3 = sync_equipment_alerts(db, "TEST-EQ-001", [], now=ANCHOR_TIME + timedelta(hours=1))
        open_count_after = db.query(Alert).filter(Alert.equipment_id == "TEST-EQ-001", Alert.status == "OPEN").count()
        assert open_count_after == 0

        resolved_count = db.query(Alert).filter(Alert.equipment_id == "TEST-EQ-001", Alert.status == "RESOLVED").count()
        assert resolved_count == 2
    finally:
        db.query(Alert).filter(Alert.equipment_id == "TEST-EQ-001").delete()
        db.query(Equipment).filter(Equipment.id == "TEST-EQ-001").delete()
        db.commit()
        db.close()
