"""
Tests for Resend email notification service and alert integration.
Verifies config-absent path, invalid-key handling, severity threshold filtering,
alert deduplication behavior, payload formatting, and error resilience.
"""
import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal, engine
from app.models import Base, Equipment, Alert
from app.analytics.anomaly_engine import AnomalyResult
from app.services.alert_service import sync_equipment_alerts
from app.services.notification_service import (
    send_alert_email,
    build_alert_email_content,
    is_severity_eligible,
    SEVERITY_WEIGHTS,
)
from app.core.config import settings


@pytest.fixture(autouse=True)
def setup_test_db():
    """Ensure database tables exist and clean up test alerts."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Ensure test equipment exists
        if not db.query(Equipment).filter(Equipment.id == "NOTIF-EQ-001").first():
            db.add(
                Equipment(
                    id="NOTIF-EQ-001",
                    type="Excavator",
                    dealer="Cat Global",
                    daily_rate=450.0,
                    metadata_json={"model": "320 GC", "serial": "CAT320-101"},
                )
            )
            db.commit()
        db.query(Alert).filter(Alert.equipment_id == "NOTIF-EQ-001").delete()
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(Alert).filter(Alert.equipment_id == "NOTIF-EQ-001").delete()
        db.commit()
    finally:
        db.close()


# -----------------------------------------------------------------------------
# 1. Config-Absent Path Tests
# -----------------------------------------------------------------------------
def test_notification_skipped_when_api_key_unset(caplog):
    """When RESEND_API_KEY is unset/empty, send_alert_email returns False and logs info."""
    with patch.object(settings, "RESEND_API_KEY", None), \
         patch.object(settings, "ALERT_NOTIFICATION_EMAIL_TO", "test@example.com"):
        with caplog.at_level(logging.INFO):
            result = send_alert_email(
                alert_type="EXCESSIVE_IDLE",
                severity="HIGH",
                message="High idle time observed (14.2h)",
                equipment_id="NOTIF-EQ-001",
            )
        assert result is False
        assert any("disabled: RESEND_API_KEY is not configured" in rec.message for rec in caplog.records)


def test_notification_skipped_when_destination_email_unset(caplog):
    """When ALERT_NOTIFICATION_EMAIL_TO is unset/empty, send_alert_email returns False and logs info."""
    with patch.object(settings, "RESEND_API_KEY", "re_test_key_123"), \
         patch.object(settings, "ALERT_NOTIFICATION_EMAIL_TO", None):
        with caplog.at_level(logging.INFO):
            result = send_alert_email(
                alert_type="EXCESSIVE_IDLE",
                severity="HIGH",
                message="High idle time observed (14.2h)",
                equipment_id="NOTIF-EQ-001",
            )
        assert result is False
        assert any("skipped: ALERT_NOTIFICATION_EMAIL_TO is not configured" in rec.message for rec in caplog.records)


# -----------------------------------------------------------------------------
# 2. Invalid-Key Path Tests
# -----------------------------------------------------------------------------
def test_invalid_api_key_fails_gracefully_without_raising(caplog):
    """When RESEND_API_KEY is invalid, Resend API error is caught, logged at ERROR, and returns False."""
    with patch.object(settings, "RESEND_API_KEY", "re_invalid_test_key_12345"), \
         patch.object(settings, "ALERT_NOTIFICATION_EMAIL_TO", "ops@rentsense.local"):
        with caplog.at_level(logging.ERROR):
            result = send_alert_email(
                alert_type="OVERDUE",
                severity="CRITICAL",
                message="Equipment 48.0h overdue",
                equipment_id="NOTIF-EQ-001",
            )
        assert result is False
        assert any("Failed to dispatch Resend alert email" in rec.message for rec in caplog.records)


# -----------------------------------------------------------------------------
# 3. Severity Threshold Filtering Tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "alert_sev,min_sev,expected",
    [
        ("CRITICAL", "MEDIUM", True),
        ("HIGH", "MEDIUM", True),
        ("WARNING", "MEDIUM", True),
        ("MEDIUM", "MEDIUM", True),
        ("LOW", "MEDIUM", False),
        ("INFO", "MEDIUM", False),
        ("LOW", "LOW", True),
        ("INFO", "INFO", True),
        ("MEDIUM", "CRITICAL", False),
        ("CRITICAL", "CRITICAL", True),
    ],
)
def test_severity_eligibility_logic(alert_sev, min_sev, expected):
    assert is_severity_eligible(alert_sev, min_sev) == expected


def test_alert_below_severity_threshold_is_skipped(caplog):
    """An alert with severity below the configured threshold should skip sending without calling Resend."""
    with patch.object(settings, "RESEND_API_KEY", "re_valid_dummy_key"), \
         patch.object(settings, "ALERT_NOTIFICATION_EMAIL_TO", "ops@rentsense.local"), \
         patch.object(settings, "ALERT_NOTIFICATION_MIN_SEVERITY", "HIGH"):
        with patch("resend.Emails.send") as mock_send:
            with caplog.at_level(logging.INFO):
                result = send_alert_email(
                    alert_type="LOW_UTILIZATION",
                    severity="LOW",
                    message="Minor low utilization signal",
                    equipment_id="NOTIF-EQ-001",
                )
            assert result is False
            mock_send.assert_not_called()
            assert any("below threshold" in rec.message for rec in caplog.records)


# -----------------------------------------------------------------------------
# 4. Alert Sync Deduplication & Notification Trigger Tests
# -----------------------------------------------------------------------------
def test_sync_equipment_alerts_triggers_notification_only_on_new_alert():
    """
    On pass 1: New alert is created -> send_alert_email is called once.
    On pass 2: Same anomaly updated in place -> send_alert_email is NOT called again.
    """
    db = SessionLocal()
    try:
        anomaly = AnomalyResult(
            equipment_id="NOTIF-EQ-001",
            anomaly_type="EXCESSIVE_IDLE",
            anomaly_score=85,
            severity="HIGH",
            explanation="14.2 hours of idle time detected.",
            supporting_signals={"idle_hours": 14.2, "utilization_rate": 0.12},
            recommended_action_category="REASSIGN",
        )

        with patch("app.services.alert_service.send_alert_email") as mock_notify:
            # Pass 1: Initial detection -> should trigger 1 email
            alerts_pass1 = sync_equipment_alerts(db, "NOTIF-EQ-001", [anomaly])
            assert len(alerts_pass1) == 1
            assert mock_notify.call_count == 1
            call_kwargs = mock_notify.call_args[1]
            assert call_kwargs["alert_type"] == "EXCESSIVE_IDLE"
            assert call_kwargs["severity"] == "HIGH"
            assert call_kwargs["equipment_id"] == "NOTIF-EQ-001"
            assert call_kwargs["anomaly_score"] == 85

            # Reset mock counter
            mock_notify.reset_mock()

            # Pass 2: Second sync pass with same open anomaly (updated in place) -> 0 emails
            updated_anomaly = AnomalyResult(
                equipment_id="NOTIF-EQ-001",
                anomaly_type="EXCESSIVE_IDLE",
                anomaly_score=88,
                severity="HIGH",
                explanation="15.0 hours of idle time detected.",
                supporting_signals={"idle_hours": 15.0, "utilization_rate": 0.10},
                recommended_action_category="REASSIGN",
            )
            alerts_pass2 = sync_equipment_alerts(db, "NOTIF-EQ-001", [updated_anomaly])
            assert len(alerts_pass2) == 1
            assert alerts_pass2[0].id == alerts_pass1[0].id  # Same DB record
            mock_notify.assert_not_called()  # Deduplicated — no new email!
    finally:
        db.close()


# -----------------------------------------------------------------------------
# 5. Outbound Resend Payload Inspection & Content Verification
# -----------------------------------------------------------------------------
def test_resend_email_payload_structure():
    """Verify that build_alert_email_content generates accurate subject, HTML, and text payloads."""
    content = build_alert_email_content(
        alert_type="EXCESSIVE_IDLE",
        severity="CRITICAL",
        message="18.5 hours idle runtime with only 1.2h active usage.",
        equipment_id="NOTIF-EQ-001",
        equipment_type="Excavator",
        dealer="Tata Hitachi Construction Machinery",
        site_name="Navi Mumbai International Airport",
        operator_name="Rajesh Sharma",
        anomaly_score=92,
        recommended_action="REASSIGN",
        timestamp=datetime(2026, 9, 2, 10, 0, 0, tzinfo=timezone.utc),
    )

    # Subject line check
    assert "[RentSense] CRITICAL Alert: NOTIF-EQ-001 (Excavator) — Excessive Idle" == content["subject"]

    # Text body content check
    assert "SEVERITY: CRITICAL" in content["text"]
    assert "EQUIPMENT: NOTIF-EQ-001 (Excavator)" in content["text"]
    assert "SITE: Navi Mumbai International Airport" in content["text"]
    assert "OPERATOR: Rajesh Sharma" in content["text"]
    assert "ANOMALY SCORE: 92/100" in content["text"]
    assert "18.5 hours idle runtime" in content["text"]
    assert "RECOMMENDED ACTION:\nReassign" in content["text"]
    assert f"{settings.FRONTEND_URL.rstrip('/')}/assets/NOTIF-EQ-001" in content["text"]

    # HTML body styling & markup check
    assert "RENTSENSE" in content["html"]
    assert "CRITICAL" in content["html"]
    assert "#dc2626" in content["html"]  # Critical red color badge
    assert "NOTIF-EQ-001" in content["html"]
    assert "Navi Mumbai International Airport" in content["html"]
    assert "Open Asset in Control Tower" in content["html"]


def test_successful_mocked_resend_send():
    """Verify that send_alert_email returns True when Resend API returns an email ID."""
    with patch.object(settings, "RESEND_API_KEY", "re_mock_valid_key_999"), \
         patch.object(settings, "ALERT_NOTIFICATION_EMAIL_TO", "fleet-lead@rentsense.com"), \
         patch.object(settings, "ALERT_NOTIFICATION_EMAIL_FROM", "RentSense Alerts <onboarding@resend.dev>"):
        with patch("resend.Emails.send", return_value={"id": "email_msg_4829104820"}) as mock_send:
            result = send_alert_email(
                alert_type="OVERDUE",
                severity="CRITICAL",
                message="Rental exceeded due date by 72 hours.",
                equipment_id="NOTIF-EQ-001",
                equipment_type="Boom Lift",
                dealer="Tata Hitachi Construction Machinery",
                site_name="Bailadila Iron Ore Complex",
                operator_name="Priya Patel",
                anomaly_score=95,
                recommended_action="RETURN",
            )
            assert result is True
            mock_send.assert_called_once()
            params = mock_send.call_args[0][0]
            assert params["to"] == ["fleet-lead@rentsense.com"]
            assert params["from"] == "RentSense Alerts <onboarding@resend.dev>"
            assert "NOTIF-EQ-001" in params["subject"]
            assert "Rental exceeded due date" in params["html"]
