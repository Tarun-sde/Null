import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import resend

from app.core.config import settings

logger = logging.getLogger(__name__)

SEVERITY_WEIGHTS: Dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "WARNING": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "INFO": 0,
}

SEVERITY_COLORS: Dict[str, str] = {
    "CRITICAL": "#dc2626",
    "HIGH": "#ea580c",
    "WARNING": "#d97706",
    "MEDIUM": "#f59e0b",
    "LOW": "#2563eb",
    "INFO": "#64748b",
}


def is_severity_eligible(alert_severity: str, min_severity: str) -> bool:
    """Check if the alert severity meets or exceeds the minimum configured severity."""
    alert_weight = SEVERITY_WEIGHTS.get(alert_severity.upper(), 1)
    min_weight = SEVERITY_WEIGHTS.get(min_severity.upper(), 2)
    return alert_weight >= min_weight


def build_alert_email_content(
    alert_type: str,
    severity: str,
    message: str,
    equipment_id: str,
    equipment_type: Optional[str] = None,
    dealer: Optional[str] = None,
    site_name: Optional[str] = None,
    operator_name: Optional[str] = None,
    anomaly_score: Optional[int] = None,
    recommended_action: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
) -> Dict[str, str]:
    """Generate subject line, HTML email body, and plain-text fallback for a newly triggered alert."""
    ts_str = (timestamp or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S UTC")
    asset_url = f"{settings.FRONTEND_URL.rstrip('/')}/assets/{equipment_id}"
    sev_upper = severity.upper()
    sev_color = SEVERITY_COLORS.get(sev_upper, "#ea580c")
    eq_type_str = equipment_type or "Heavy Machinery"
    site_str = site_name or "Unassigned / Depot Yard"
    op_str = operator_name or "Unassigned"
    score_str = f"{anomaly_score}/100" if anomaly_score is not None else "N/A"
    rec_action_str = (recommended_action or "Review in Control Tower").replace("_", " ").title()

    subject = f"[RentSense] {sev_upper} Alert: {equipment_id} ({eq_type_str}) — {alert_type.replace('_', ' ').title()}"

    # Plain text version
    text_body = f"""==================================================
RENTSENSE CONTROL TOWER — FLEET ANOMALY ALERT
==================================================

SEVERITY: {sev_upper}
EQUIPMENT: {equipment_id} ({eq_type_str})
DEALER: {dealer or 'Unknown'}
ALERT TYPE: {alert_type}
ANOMALY SCORE: {score_str}
SITE: {site_str}
OPERATOR: {op_str}
TIMESTAMP: {ts_str}

EXPLANATION:
{message}

RECOMMENDED ACTION:
{rec_action_str}

VIEW ASSET IN CONTROL TOWER:
{asset_url}

--------------------------------------------------
RentSense Fleet Intelligence OS · Automated Alert Notification
"""

    # Rich responsive HTML template
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #18181b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f4f4f5; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" max-width="600" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 16px; border: 1px solid #e4e4e7; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); overflow: hidden;">
          
          <!-- Brand Header -->
          <tr>
            <td style="background-color: #09090b; padding: 24px 32px; border-bottom: 1px solid #27272a;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <div style="display: inline-block; vertical-align: middle; width: 12px; height: 12px; background-color: #ff5a24; border-radius: 2px; margin-right: 10px;"></div>
                    <span style="display: inline-block; vertical-align: middle; color: #ffffff; font-size: 16px; font-weight: 700; letter-spacing: 0.18em;">RENTSENSE</span>
                    <span style="display: block; color: #a1a1aa; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 4px; font-weight: 500;">Fleet Intelligence OS</span>
                  </td>
                  <td align="right">
                    <span style="display: inline-block; background-color: {sev_color}20; color: {sev_color}; border: 1px solid {sev_color}40; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">
                      {sev_upper}
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Main Alert Banner -->
          <tr>
            <td style="padding: 32px 32px 20px 32px;">
              <h1 style="margin: 0 0 8px 0; font-size: 22px; font-weight: 600; color: #09090b; line-height: 1.3;">
                New Anomaly Detected on {equipment_id}
              </h1>
              <p style="margin: 0; font-size: 14px; color: #71717a; line-height: 1.5;">
                RentSense Anomaly Engine detected an operational condition requiring operator attention.
              </p>
            </td>
          </tr>

          <!-- Message Callout Box -->
          <tr>
            <td style="padding: 0 32px 24px 32px;">
              <div style="background-color: #fafafa; border-left: 4px solid {sev_color}; border-radius: 0 8px 8px 0; padding: 16px 20px; border-top: 1px solid #f4f4f5; border-right: 1px solid #f4f4f5; border-bottom: 1px solid #f4f4f5;">
                <p style="margin: 0 0 6px 0; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #52525b;">Diagnostic Explanation</p>
                <p style="margin: 0; font-size: 14px; color: #18181b; line-height: 1.5; font-weight: 500;">{message}</p>
              </div>
            </td>
          </tr>

          <!-- Metadata Grid -->
          <tr>
            <td style="padding: 0 32px 28px 32px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border: 1px solid #e4e4e7; border-radius: 10px; overflow: hidden; font-size: 13px;">
                <tr style="background-color: #fbfbfb;">
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600; width: 38%; border-bottom: 1px solid #e4e4e7;">Asset Identifier</td>
                  <td style="padding: 12px 16px; color: #09090b; font-weight: 700; border-bottom: 1px solid #e4e4e7; font-family: monospace;">{equipment_id}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600; border-bottom: 1px solid #e4e4e7;">Equipment Type</td>
                  <td style="padding: 12px 16px; color: #09090b; border-bottom: 1px solid #e4e4e7;">{eq_type_str} ({dealer or 'Depot'})</td>
                </tr>
                <tr style="background-color: #fbfbfb;">
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600; border-bottom: 1px solid #e4e4e7;">Alert Classification</td>
                  <td style="padding: 12px 16px; color: #09090b; font-weight: 600; border-bottom: 1px solid #e4e4e7;">{alert_type.replace('_', ' ')}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600; border-bottom: 1px solid #e4e4e7;">Anomaly Score</td>
                  <td style="padding: 12px 16px; color: #09090b; font-weight: 600; border-bottom: 1px solid #e4e4e7;">{score_str}</td>
                </tr>
                <tr style="background-color: #fbfbfb;">
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600; border-bottom: 1px solid #e4e4e7;">Job Site Location</td>
                  <td style="padding: 12px 16px; color: #09090b; border-bottom: 1px solid #e4e4e7;">{site_str}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600; border-bottom: 1px solid #e4e4e7;">Assigned Operator</td>
                  <td style="padding: 12px 16px; color: #09090b; border-bottom: 1px solid #e4e4e7;">{op_str}</td>
                </tr>
                <tr style="background-color: #fbfbfb;">
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600; border-bottom: 1px solid #e4e4e7;">Recommended Action</td>
                  <td style="padding: 12px 16px; color: #ff5a24; font-weight: 700; border-bottom: 1px solid #e4e4e7;">{rec_action_str}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 16px; color: #71717a; font-weight: 600;">Detection Timestamp</td>
                  <td style="padding: 12px 16px; color: #09090b;">{ts_str}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA Button -->
          <tr>
            <td align="center" style="padding: 0 32px 36px 32px;">
              <a href="{asset_url}" target="_blank" style="display: inline-block; background-color: #09090b; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 10px; font-size: 14px; font-weight: 600; letter-spacing: 0.02em; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                Open Asset in Control Tower &rarr;
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #fbfbfb; padding: 20px 32px; border-top: 1px solid #e4e4e7; text-align: center;">
              <p style="margin: 0; font-size: 11px; color: #a1a1aa; line-height: 1.5;">
                This automated operational notification was dispatched by the RentSense Fleet Telemetry & Anomaly Surveillance Engine.<br>
                Configured destination: <span style="color: #71717a;">{settings.ALERT_NOTIFICATION_EMAIL_TO or 'Unset'}</span>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    return {
        "subject": subject,
        "html": html_body,
        "text": text_body,
    }


def send_alert_email(
    alert_type: str,
    severity: str,
    message: str,
    equipment_id: str,
    equipment_type: Optional[str] = None,
    dealer: Optional[str] = None,
    site_name: Optional[str] = None,
    operator_name: Optional[str] = None,
    anomaly_score: Optional[int] = None,
    recommended_action: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
) -> bool:
    """
    Send an email notification for a newly created anomaly alert using Resend.
    
    Safe Fail-Fast Rules:
    - Returns False if RESEND_API_KEY or ALERT_NOTIFICATION_EMAIL_TO is not configured.
    - Returns False if alert severity is below ALERT_NOTIFICATION_MIN_SEVERITY threshold.
    - Never raises exceptions: logs errors and returns False so alert processing is never blocked.
    """
    # 1. Check if email notifications are enabled and configured
    api_key = settings.RESEND_API_KEY
    to_email = settings.ALERT_NOTIFICATION_EMAIL_TO

    if not api_key or not api_key.strip():
        logger.info("[NOTIFICATION] Resend email notifications disabled: RESEND_API_KEY is not configured.")
        return False

    if not to_email or not to_email.strip():
        logger.info("[NOTIFICATION] Resend email notifications skipped: ALERT_NOTIFICATION_EMAIL_TO is not configured.")
        return False

    # 2. Check severity threshold
    min_severity = settings.ALERT_NOTIFICATION_MIN_SEVERITY or "MEDIUM"
    if not is_severity_eligible(severity, min_severity):
        logger.info(
            f"[NOTIFICATION] Alert email skipped for {equipment_id}: severity '{severity}' is below threshold '{min_severity}'."
        )
        return False

    # 3. Build email payload
    content = build_alert_email_content(
        alert_type=alert_type,
        severity=severity,
        message=message,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        dealer=dealer,
        site_name=site_name,
        operator_name=operator_name,
        anomaly_score=anomaly_score,
        recommended_action=recommended_action,
        metadata=metadata,
        timestamp=timestamp,
    )

    from_email = settings.ALERT_NOTIFICATION_EMAIL_FROM or "RentSense Alerts <onboarding@resend.dev>"

    # 4. Dispatch via Resend SDK
    try:
        resend.api_key = api_key.strip()
        params: resend.Emails.SendParams = {
            "from": from_email,
            "to": [to_email.strip()],
            "subject": content["subject"],
            "html": content["html"],
            "text": content["text"],
        }
        response = resend.Emails.send(params)

        email_id = None
        if isinstance(response, dict):
            email_id = response.get("id")
        elif hasattr(response, "id"):
            email_id = getattr(response, "id")

        if email_id or response:
            logger.info(
                f"[NOTIFICATION] Alert email successfully sent via Resend for {equipment_id} ({severity} {alert_type}). Resend ID: {email_id}"
            )
            return True
        else:
            logger.warning(
                f"[NOTIFICATION] Resend email call completed but returned unexpected response for {equipment_id}: {response}"
            )
            return False

    except Exception as e:
        logger.error(
            f"[NOTIFICATION] Failed to dispatch Resend alert email for {equipment_id} ({severity} {alert_type}): {e}"
        )
        return False
