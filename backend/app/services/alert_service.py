from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Alert
from app.analytics.anomaly_engine import AnomalyResult


def sync_equipment_alerts(
    db: Session,
    equipment_id: str,
    anomalies: List[AnomalyResult],
    now: Optional[datetime] = None,
) -> List[Alert]:
    """
    Synchronize detected anomalies with the alerts table using deterministic deduplication.
    - If an anomaly is currently active:
      - Updates existing OPEN alert message, severity, and metadata_json (in-place).
      - Or inserts a new Alert record if none exists.
    - If a previously OPEN alert's condition is no longer present in anomalies:
      - Resolves the alert (sets status='RESOLVED', resolved_at=now).
    """
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    # 1. Fetch currently open alerts for this equipment
    open_alerts = (
        db.query(Alert)
        .filter(Alert.equipment_id == equipment_id, Alert.status == "OPEN")
        .all()
    )
    open_alerts_by_type = {a.alert_type: a for a in open_alerts}

    active_anomaly_types = set()
    synced_alerts = []

    # 2. Process active anomalies
    for anomaly in anomalies:
        active_anomaly_types.add(anomaly.anomaly_type)
        if anomaly.anomaly_type in open_alerts_by_type:
            # Update existing alert (deduplication)
            existing_alert = open_alerts_by_type[anomaly.anomaly_type]
            existing_alert.message = anomaly.explanation
            existing_alert.severity = anomaly.severity
            existing_alert.metadata_json = {
                **anomaly.supporting_signals,
                "anomaly_score": anomaly.anomaly_score,
                "recommended_action": anomaly.recommended_action_category,
                "last_evaluated_at": current_time.isoformat(),
            }
            synced_alerts.append(existing_alert)
        else:
            # Insert new alert
            new_alert = Alert(
                equipment_id=equipment_id,
                alert_type=anomaly.anomaly_type,
                severity=anomaly.severity,
                message=anomaly.explanation,
                status="OPEN",
                metadata_json={
                    **anomaly.supporting_signals,
                    "anomaly_score": anomaly.anomaly_score,
                    "recommended_action": anomaly.recommended_action_category,
                },
                created_at=current_time,
                resolved_at=None,
            )
            db.add(new_alert)
            synced_alerts.append(new_alert)

    # 3. Auto-resolve alerts whose condition has cleared (excluding non-anomaly system alerts)
    managed_anomaly_types = {
        "EXCESSIVE_IDLE",
        "IDLE",
        "ZERO_RUNTIME",
        "MISSING_ASSIGNMENT",
        "OVERDUE",
        "LOW_UTILIZATION",
    }
    for alert_type, open_alert in open_alerts_by_type.items():
        if alert_type in managed_anomaly_types and alert_type not in active_anomaly_types:
            open_alert.status = "RESOLVED"
            open_alert.resolved_at = current_time

    db.commit()
    for alert in synced_alerts:
        db.refresh(alert)

    return synced_alerts
