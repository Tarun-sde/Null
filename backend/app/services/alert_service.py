import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Alert, Equipment
from app.analytics.anomaly_engine import AnomalyResult
from app.services.equipment_service import get_current_rental
from app.services.notification_service import send_alert_email

logger = logging.getLogger(__name__)


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
    - Dispatches email notification via Resend ONLY for newly created alerts (after DB commit).
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
    newly_created_alerts = []

    # 2. Process active anomalies
    for anomaly in anomalies:
        active_anomaly_types.add(anomaly.anomaly_type)
        if anomaly.anomaly_type in open_alerts_by_type:
            # Update existing alert (deduplication — does not re-trigger new alert email)
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
            # Insert genuinely new alert
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
            newly_created_alerts.append((new_alert, anomaly))

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

    # 4. Dispatch email notification for genuinely NEW alerts after successful DB commit
    if newly_created_alerts:
        try:
            equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
            eq_type = equipment.type if equipment else None
            dealer = equipment.dealer if equipment else None
            rental = get_current_rental(equipment) if equipment else None
            site_name = rental.site.name if (rental and rental.site) else None
            operator_name = rental.operator.name if (rental and rental.operator) else None

            for alert_obj, anomaly_obj in newly_created_alerts:
                send_alert_email(
                    alert_type=alert_obj.alert_type,
                    severity=alert_obj.severity,
                    message=alert_obj.message,
                    equipment_id=equipment_id,
                    equipment_type=eq_type,
                    dealer=dealer,
                    site_name=site_name,
                    operator_name=operator_name,
                    anomaly_score=anomaly_obj.anomaly_score if anomaly_obj else None,
                    recommended_action=anomaly_obj.recommended_action_category if anomaly_obj else None,
                    metadata=alert_obj.metadata_json,
                    timestamp=alert_obj.created_at,
                )
        except Exception as notify_err:
            # Best-effort notification: failure to notify must never break the alert sync
            logger.warning(f"[NOTIFICATION] Non-fatal notification error during alert sync for {equipment_id}: {notify_err}")

    return synced_alerts
