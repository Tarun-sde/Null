# RentSense Email Notifications via Resend

RentSense Control Tower includes real-time automated email notifications for newly detected fleet anomaly alerts (e.g. excessive idle, overdue rentals, missing operator assignments, low utilization) powered by [Resend](https://resend.com).

---

## 1. Getting a Resend API Key

1. Sign up for a free account at [resend.com](https://resend.com) (free tier includes **3,000 emails/month** and **100 emails/day**).
2. Confirm your email address.
3. In the Resend Dashboard, go to **API Keys** &rarr; click **Create API Key** (name it e.g. `RentSense Control Tower` with `Sending access`).
4. Copy the API key (starts with `re_`).

---

## 2. Sandbox vs. Production Domain

- **Sandbox Testing (Default)**:
  - You can start testing immediately without verifying a custom domain using Resend's default sender: `RentSense Alerts <onboarding@resend.dev>`.
  - **Important Limitation**: In sandbox mode, Resend **only delivers emails to the verified email address of your Resend account owner**. Set `ALERT_NOTIFICATION_EMAIL_TO` to that exact email.
- **Custom Domain (Production)**:
  - Add and verify your own DNS domain (e.g., `notifications.yourdomain.com`) in the Resend dashboard.
  - Once verified, you can update `ALERT_NOTIFICATION_EMAIL_FROM` to `RentSense Alerts <alerts@yourdomain.com>` and send to any recipient.

---

## 3. Configuration Variables (`.env`)

Add or update the following variables in your `.env` file:

| Variable | Required / Secret | Default Value | Description | If Left Blank |
|---|---|---|---|---|
| `RESEND_API_KEY` | Optional / **Secret** | *None* | Your Resend API key (`re_...`) | Email notifications are **safely disabled**; no errors raised. |
| `ALERT_NOTIFICATION_EMAIL_TO` | Optional / Public | *None* | Destination email address to receive alert notifications | Email dispatch is skipped with an info log line. |
| `ALERT_NOTIFICATION_EMAIL_FROM` | Optional / Public | `RentSense Alerts <onboarding@resend.dev>` | Display sender name and email | Uses default Resend sandbox sender address. |
| `ALERT_NOTIFICATION_MIN_SEVERITY` | Optional / Public | `MEDIUM` | Minimum severity threshold (`CRITICAL`, `HIGH`, `WARNING`, `MEDIUM`, `LOW`, `INFO`) | Defaults to `MEDIUM` (skips trivial/info signals). |

---

## 4. How to Trigger a Test Alert & Email

Once you have added your `RESEND_API_KEY` and `ALERT_NOTIFICATION_EMAIL_TO` to `.env`:

1. **Restart the Backend Container**:
   ```bash
   docker compose restart backend
   ```

2. **Trigger an Anomaly via Telemetry Ingestion**:
   Send a telemetry packet for an asset that triggers an `EXCESSIVE_IDLE` anomaly (e.g., 16 hours of engine runtime with 15 hours of idle time):

   ```bash
   curl -X POST http://localhost/api/v1/telemetry \
     -H "Content-Type: application/json" \
     -d '{
       "equipment_id": "EQX1001",
       "latitude": 37.7749,
       "longitude": -122.4194,
       "engine_hours": 30.0,
       "idle_hours": 22.0,
       "fuel_pct": 65.0
     }'
   ```

3. **Check Your Inbox & Backend Logs**:
   - Check your destination email inbox for the formatted alert email.
   - Or view the container logs:
     ```bash
     docker logs rentsense-backend | grep "\[NOTIFICATION\]"
     ```
     You will see:
     `[INFO] app.services.notification_service: [NOTIFICATION] Alert email successfully sent via Resend for EQX1001 (HIGH EXCESSIVE_IDLE). Resend ID: email_...`

---

## 5. Architectural Guarantees

- **No Duplicates**: Email notifications are triggered **only when a new alert is created**. Subsequent sync passes on existing open alerts update metrics in place and will not spam your inbox.
- **Fail-Safe & Non-Blocking**: If Resend is unreachable, invalid, or rate-limited, the error is logged and the core RentSense application continues operating normally without interruption.
