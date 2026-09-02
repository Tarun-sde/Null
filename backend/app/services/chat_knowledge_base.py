"""
Static Knowledge Base for the RentSense AI Assistant.
Sourced strictly from actual RentSense code, models, threshold constants, and business logic.
Provides grounded facts for general application help and operational explanations.
"""

RENTSENSE_APP_KNOWLEDGE_BASE = """
================================================================================
RENTSENSE CONTROL TOWER — SYSTEM ARCHITECTURE & OPERATIONAL KNOWLEDGE BASE
================================================================================

1. OVERVIEW & MISSION
--------------------------------------------------------------------------------
RentSense is an autonomous heavy equipment fleet surveillance and ROI intelligence platform designed for construction contractors and rental fleet operators. It continuously monitors machine telemetry, detects underutilization and contract anomalies, recommends high-leverage operational handoffs (returns, reassignments), and tracks realized financial savings in an immutable impact ledger.

2. ASSET STATUS DEFINITIONS & DETERMINISTIC RULES
--------------------------------------------------------------------------------
Every piece of machinery in RentSense has a deterministic status derived from its active rental contract and real-time telemetry:

- ACTIVE: Machine is actively checked out on a rental contract with a verified site and operator, operating within normal utilization and scheduling parameters.
- IDLE: Machine is rented but failing utilization criteria. Triggered if:
    a) Continuous idle engine hours >= 8.0 hours (IDLE_HOURS_THRESHOLD = 8.0h), OR
    b) Utilization rate < 20% (LOW_UTILIZATION_THRESHOLD = 0.20), where utilization = (engine_hours - idle_hours) / engine_hours.
- DUE_SOON: Machine is on an active rental and its scheduled return time (`due_at`) is within the next 48 hours (ALERT_DUE_SOON_HOURS = 48h).
- OVERDUE: Machine is on an active rental and current time has passed its scheduled return time (`now > due_at`).
- UNASSIGNED: Machine has no open rental contract (sitting in the depot yard ready for deployment) OR has an active contract missing an assigned operator or site.
- RETURNED: Machine has completed its rental contract, undergone return check-in inspection, and closed its rental timeline.

Status Precedence Order: OVERDUE > DUE_SOON > IDLE > ACTIVE > UNASSIGNED.

3. ANOMALY DETECTION ENGINE & SCORING RULES
--------------------------------------------------------------------------------
RentSense's Anomaly Engine continuously inspects equipment telemetry and rental metadata using explainable, deterministic rules (no black-box hallucinations):

- EXCESSIVE_IDLE:
    * Condition: Telemetry `idle_hours >= 8.0h` under an active rental.
    * Score Calculation: 40 + min(50, floor(idle_hours * 3)) -> range 40..90.
    * Severity: CRITICAL if score >= 70, WARNING if score between 40..69.
    * Recommended Action: REASSIGN_EQUIPMENT to another job site with pending demand.

- LOW_UTILIZATION:
    * Condition: Telemetry `engine_hours >= 1.0h` and `utilization < 0.20` (20%).
    * Score Calculation: 50 + min(45, floor((0.20 - utilization) * 200)) -> range 50..95.
    * Severity: CRITICAL if score >= 70, WARNING if score between 40..69.
    * Recommended Action: REASSIGN_EQUIPMENT.

- OVERDUE:
    * Condition: Active rental `now > due_at`.
    * Score Calculation: 60 + min(40, floor(days_overdue * 10)) -> range 60..100.
    * Severity: CRITICAL (score >= 70).
    * Recommended Action: RETURN_EQUIPMENT to depot or EXTEND_RENTAL.

- MISSING_ASSIGNMENT:
    * Condition: Active rental record exists with null `operator_id` or null `site_id`.
    * Score Calculation: Fixed 75.
    * Severity: CRITICAL.
    * Recommended Action: INVESTIGATE_ASSIGNMENT.

- ZERO_RUNTIME:
    * Condition: Checked-out equipment deployed > 24 hours with engine_hours == 0.0.
    * Score Calculation: Fixed 65.
    * Severity: WARNING.
    * Recommended Action: INVESTIGATE_DEPLOYMENT.

Severity Thresholds:
- Score >= 70 -> CRITICAL
- Score 40..69 -> WARNING / HIGH
- Score 1..39 -> INFO / LOW

4. OPERATIONAL WORKFLOWS & UI PROCEDURES
--------------------------------------------------------------------------------
- Checking Out Equipment:
    1. Navigate to `/scan` or open the target asset detail page `/assets/{id}`.
    2. Click "Check Out" button to open the Checkout Modal.
    3. Select target Job Site, Operator, Scheduled Return Date (`due_at`), Daily Rate, and condition notes.
    4. Submit: Creates an active `Rental` record, logs an immutable `CHECKOUT` Audit Event, and transitions equipment status to `ACTIVE`.

- Checking In Equipment (Off-Rent):
    1. Navigate to `/scan` or open the asset detail page `/assets/{id}`.
    2. Click "Check In" button.
    3. Record return condition (e.g. "Good", "Needs Cleaning"), fuel level, and return inspection notes.
    4. Submit: Closes the active `Rental` (`checked_in_at = now`), logs a `CHECKIN` Audit Event, auto-resolves open alerts for this unit, and transitions status to `UNASSIGNED` in yard.

- QR Scanning & Rapid Lookup:
    1. Navigate to `/scan`.
    2. Enter or scan any equipment asset QR tag (e.g. `EQX1001`, `EQX1007`).
    3. The system instantly loads asset status, assigned site/operator, telemetry stats, and one-click Check In / Check Out controls.

- Executing Recommendations from Actions Queue:
    1. Navigate to `/actions`.
    2. View prioritized action queue (RETURN, REASSIGN, INVESTIGATE).
    3. Click "Execute Action" / "Complete Action".
    4. When marked COMPLETED, RentSense automatically executes the business state transition (e.g., closing rental or reassigning site), resolves associated open alerts, and creates an immutable `ImpactRecord` capturing realized cost savings.

- Adding New Equipment:
    1. Navigate to `/assets` and click "+ Add Equipment".
    2. Fill in Equipment ID, Machine Type, Dealer, Daily Rental Rate, Model, and Serial Number.
    3. Submit: Validates uniqueness, provisions QR identifier metadata, saves to database, and registers with simulator dynamic discovery.

5. FINANCIAL IMPACT & ROI CALCULATIONS
--------------------------------------------------------------------------------
RentSense calculates real-time avoided costs and realized savings using mathematical financial formulas in Indian Rupees (INR / ₹):

- Idle Avoidance Savings (REASSIGN):
    Formula: `avoidable_idle_days * daily_rate`
    where `avoidable_idle_days = round((idle_hours - 4.0) / 8.0, 1)` (minimum 0.5 days).
    Example: 14.2h idle excavator at ₹18,500/day = 1.8 avoidable days * ₹18,500 = ₹33,300 saved.

- Overdue Surcharge Avoided (RETURN):
    Formula: `days_overdue * daily_rate`
    where `days_overdue = round(overdue_hours / 24.0, 1)`.
    Example: 48.0h overdue lift at ₹7,500/day = 2.0 days * ₹7,500 = ₹15,000 saved.

- Standby Recovery (UNASSIGNED):
    Formula: `standby_days * daily_rate`.

- Realized Savings vs Estimated Impact:
    * Estimated Impact: Projected financial loss if the anomaly is left unaddressed.
    * Realized Savings: Actual hard-rupee cost avoided once an operator executes and completes the recommendation in the Actions Queue.

6. PREDICTIVE DEMAND FORECASTING
--------------------------------------------------------------------------------
- Algorithm: Deterministic Weighted Moving Average (WMA) combining:
    * Recent 30-day utilization & demand trends (50% weight)
    * Mid-term 60-day historical averages (30% weight)
    * Long-term 90-day seasonal baseline (20% weight)
- Model Confidence Score: Calibrated using historical Mean Absolute Error (MAE) and data density. High sample size (>30 data points) yields calibrated confidence (85-98%).
- Purpose: Identifies which machine categories (Excavators, Cranes, Lifts, Loaders) will experience upcoming shortages or surplus across project sites over 7, 14, and 30 day horizons.

7. APPLICATION NAVIGATION & PAGES
--------------------------------------------------------------------------------
- `/dashboard`: High-density command center with live fleet KPI cards, radar surveillance map, telemetry activity timeline, open alerts panel, and top recommendations.
- `/assets`: Complete equipment catalog with Grid Cards and Table Ledger views, status filters, search, and Add Equipment modal.
- `/assets/{id}`: Detailed asset cockpit with live engine/idle/fuel sparklines, OpenStreetMap location tracker, active rental contract details, and tamper-evident audit timeline.
- `/scan`: Mobile-optimized QR barcode scanner and rapid handoff console for field technicians.
- `/actions`: Operational dispatch queue to review, approve, execute, or cancel recommended fleet adjustments.
- `/forecast`: Predictive demand modeling dashboard with backtested MAE error metrics and equipment allocation recommendations.
- `/impact`: Financial ROI analytics ledger showing total realized savings, avoided cost breakdown by action type, site, and equipment category.
- `/login`: Secure JWT authentication login screen.

8. SECURITY & READ-ONLY ASSISTANT POLICY
--------------------------------------------------------------------------------
- The AI Assistant is strictly READ-ONLY.
- It can NEVER check in/out equipment, cancel actions, resolve alerts, or alter database records.
- If asked to perform a mutation, the assistant politely explains the exact UI steps for the user to execute the action safely in the Control Tower.
"""
