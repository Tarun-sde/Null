import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.models import (
    Base,
    Equipment,
    Site,
    Operator,
    Rental,
    Telemetry,
    Alert,
    Forecast,
    Recommendation,
    AuditEvent,
)

# Deterministic anchor timestamp
ANCHOR_TIME = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)


def reset_database(db: Session):
    """
    Reset demo database tables.
    Works across PostgreSQL (TRUNCATE) and SQLite (DELETE).
    """
    dialect_name = db.bind.dialect.name if db.bind else "sqlite"
    if dialect_name == "postgresql":
        db.execute(text("TRUNCATE TABLE audit_events, recommendations, forecasts, alerts, telemetry, rentals, operators, sites, equipment RESTART IDENTITY CASCADE;"))
        db.commit()
    else:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()


def seed_database(db: Session, reset: bool = True, anchor_time: datetime = ANCHOR_TIME):
    """
    Deterministic & Idempotent Database Seeder.
    Seeds the 7 challenge equipment assets, 3 sites, 4 operators,
    associated rental scenarios, telemetry streams, and audit history.
    """
    if reset:
        reset_database(db)

    base_time = anchor_time

    # 1. Seed Sites (3 realistic construction sites)
    sites_data = [
        {
            "id": "SITE-001",
            "name": "Metro Tunnel Extension",
            "location": "Sector 4 Downtown Transit Corridor",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "created_at": base_time - timedelta(days=60),
        },
        {
            "id": "SITE-002",
            "name": "Northside Logistics Hub",
            "location": "Terminal B Port Industrial Zone",
            "latitude": 37.8044,
            "longitude": -122.2712,
            "created_at": base_time - timedelta(days=45),
        },
        {
            "id": "SITE-003",
            "name": "Highland Medical Center",
            "location": "Upper Ridge Medical Campus",
            "latitude": 37.7600,
            "longitude": -122.4470,
            "created_at": base_time - timedelta(days=30),
        },
    ]

    for s_data in sites_data:
        existing = db.query(Site).filter(Site.id == s_data["id"]).first()
        if not existing:
            db.add(Site(**s_data))

    db.flush()

    # 2. Seed Operators (4 realistic heavy machinery operators)
    operators_data = [
        {
            "id": "OP-001",
            "name": "Marcus Vance",
            "contact": "m.vance@constructco.demo | (555) 234-5678",
            "created_at": base_time - timedelta(days=90),
        },
        {
            "id": "OP-002",
            "name": "Elena Rostova",
            "contact": "e.rostova@heavyworks.demo | (555) 345-6789",
            "created_at": base_time - timedelta(days=90),
        },
        {
            "id": "OP-003",
            "name": "Devon Cole",
            "contact": "d.cole@metrobuild.demo | (555) 456-7890",
            "created_at": base_time - timedelta(days=75),
        },
        {
            "id": "OP-004",
            "name": "Sarah Jenkins",
            "contact": "s.jenkins@apexops.demo | (555) 567-8901",
            "created_at": base_time - timedelta(days=60),
        },
    ]

    for o_data in operators_data:
        existing = db.query(Operator).filter(Operator.id == o_data["id"]).first()
        if not existing:
            db.add(Operator(**o_data))

    db.flush()

    # 3. Seed Challenge Equipment (EQX1001 - EQX1007)
    equipment_data = [
        {
            "id": "EQX1001",
            "type": "Excavator",
            "dealer": "Cat Rentals",
            "daily_rate": 450.0,
            "metadata_json": {"model": "CAT 320 GC", "serial": "CAT320-9941", "qr_code": "EQX1001"},
            "created_at": base_time - timedelta(days=20),
        },
        {
            "id": "EQX1002",
            "type": "Bulldozer",
            "dealer": "United Rentals",
            "daily_rate": 650.0,
            "metadata_json": {"model": "Komatsu D61PXi", "serial": "KOM61-3821", "qr_code": "EQX1002"},
            "created_at": base_time - timedelta(days=15),
        },
        {
            "id": "EQX1003",
            "type": "Wheel Loader",
            "dealer": "Sunbelt Rentals",
            "daily_rate": 380.0,
            "metadata_json": {"model": "Deere 544 P-Tier", "serial": "JD544-7712", "qr_code": "EQX1003"},
            "created_at": base_time - timedelta(days=18),
        },
        {
            "id": "EQX1004",
            "type": "Generator",
            "dealer": "Herc Rentals",
            "daily_rate": 220.0,
            "metadata_json": {"model": "MQ Power 150kVA", "serial": "MQP150-1094", "qr_code": "EQX1004"},
            "created_at": base_time - timedelta(days=12),
        },
        {
            "id": "EQX1005",
            "type": "Bulldozer",
            "dealer": "Cat Rentals",
            "daily_rate": 850.0,
            "metadata_json": {"model": "CAT D8T Heavy", "serial": "CATD8-8823", "qr_code": "EQX1005"},
            "created_at": base_time - timedelta(days=25),
        },
        {
            "id": "EQX1006",
            "type": "Scissor Lift",
            "dealer": "Sunbelt Rentals",
            "daily_rate": 180.0,
            "metadata_json": {"model": "Genie GS-3246", "serial": "GEN32-4419", "qr_code": "EQX1006"},
            "created_at": base_time - timedelta(days=30),
        },
        {
            "id": "EQX1007",
            "type": "Boom Lift",
            "dealer": "United Rentals",
            "daily_rate": 420.0,
            "metadata_json": {"model": "JLG 600AJ", "serial": "JLG600-5520", "qr_code": "EQX1007"},
            "created_at": base_time - timedelta(days=10),
        },
    ]

    for eq_data in equipment_data:
        existing = db.query(Equipment).filter(Equipment.id == eq_data["id"]).first()
        if not existing:
            db.add(Equipment(**eq_data))

    db.flush()

    # 4. Seed Rentals (Creating the exact required scenarios)
    rentals_data = [
        # EQX1001: Under-utilized (Active rental at SITE-001, OP-001, high idle hours)
        {
            "equipment_id": "EQX1001",
            "site_id": "SITE-001",
            "operator_id": "OP-001",
            "checked_out_at": base_time - timedelta(days=5),
            "due_at": base_time + timedelta(days=10),
            "checked_in_at": None,
            "daily_rate": 450.0,
            "condition_notes": "Delivered in good working order. Foundation excavation phase.",
            "created_at": base_time - timedelta(days=5),
        },
        # EQX1002: Missing Assignment (Checked out to SITE-002 with operator_id=None)
        {
            "equipment_id": "EQX1002",
            "site_id": "SITE-002",
            "operator_id": None,
            "checked_out_at": base_time - timedelta(days=2),
            "due_at": base_time + timedelta(days=8),
            "checked_in_at": None,
            "daily_rate": 650.0,
            "condition_notes": "Delivered to staging area. Operator assignment pending.",
            "created_at": base_time - timedelta(days=2),
        },
        # EQX1003: Active Normal (Healthy active rental at SITE-001, OP-002)
        {
            "equipment_id": "EQX1003",
            "site_id": "SITE-001",
            "operator_id": "OP-002",
            "checked_out_at": base_time - timedelta(days=4),
            "due_at": base_time + timedelta(days=7),
            "checked_in_at": None,
            "daily_rate": 380.0,
            "condition_notes": "Active in material handling and earth movement.",
            "created_at": base_time - timedelta(days=4),
        },
        # EQX1004: Due Soon (Due within 20 hours < 48h threshold at SITE-002, OP-003)
        {
            "equipment_id": "EQX1004",
            "site_id": "SITE-002",
            "operator_id": "OP-003",
            "checked_out_at": base_time - timedelta(days=6),
            "due_at": base_time + timedelta(hours=20),
            "checked_in_at": None,
            "daily_rate": 220.0,
            "condition_notes": "Temporary power for site trailers and night lighting.",
            "created_at": base_time - timedelta(days=6),
        },
        # EQX1005: High-Use (Active heavy bulldozer with 48h engine runtime at SITE-002, OP-004)
        {
            "equipment_id": "EQX1005",
            "site_id": "SITE-002",
            "operator_id": "OP-004",
            "checked_out_at": base_time - timedelta(days=8),
            "due_at": base_time + timedelta(days=12),
            "checked_in_at": None,
            "daily_rate": 850.0,
            "condition_notes": "High-intensity site grading and land clearing.",
            "created_at": base_time - timedelta(days=8),
        },
        # EQX1006: Overdue (Due 2 days ago at SITE-003, OP-001)
        {
            "equipment_id": "EQX1006",
            "site_id": "SITE-003",
            "operator_id": "OP-001",
            "checked_out_at": base_time - timedelta(days=10),
            "due_at": base_time - timedelta(days=2),
            "checked_in_at": None,
            "daily_rate": 180.0,
            "condition_notes": "Electrical and HVAC ductwork installation.",
            "created_at": base_time - timedelta(days=10),
        },
        # EQX1007: Unassigned (Previous rental completed and checked in 3 days ago, now in yard)
        {
            "equipment_id": "EQX1007",
            "site_id": "SITE-003",
            "operator_id": "OP-003",
            "checked_out_at": base_time - timedelta(days=9),
            "due_at": base_time - timedelta(days=4),
            "checked_in_at": base_time - timedelta(days=3),
            "daily_rate": 420.0,
            "condition_notes": "Returned clean, full tank, parked in yard staging area.",
            "created_at": base_time - timedelta(days=9),
        },
    ]

    for r_data in rentals_data:
        existing = (
            db.query(Rental)
            .filter(
                Rental.equipment_id == r_data["equipment_id"],
                Rental.checked_out_at == r_data["checked_out_at"],
            )
            .first()
        )
        if not existing:
            db.add(Rental(**r_data))

    db.flush()

    # 5. Seed Historical Telemetry Streams
    telemetry_profiles = {
        # EQX1001: Low Utilization / High Idle (14.2h idle out of 16.0h total -> 11.2% utilization < 20%)
        "EQX1001": {
            "lat": 37.7750, "lng": -122.4190,
            "engine_base": 16.0, "idle_base": 14.2, "fuel": 82.0
        },
        # EQX1002: Missing assignment (Stationary at staging yard, 2.0h engine, 1.8h idle)
        "EQX1002": {
            "lat": 37.8040, "lng": -122.2710,
            "engine_base": 2.0, "idle_base": 1.8, "fuel": 95.0
        },
        # EQX1003: Active Normal (28.5h engine, 4.2h idle -> 85.3% utilization)
        "EQX1003": {
            "lat": 37.7752, "lng": -122.4198,
            "engine_base": 28.5, "idle_base": 4.2, "fuel": 68.0
        },
        # EQX1004: Due Soon Generator (34.0h engine, 2.1h idle -> 93.8% utilization)
        "EQX1004": {
            "lat": 37.8048, "lng": -122.2715,
            "engine_base": 34.0, "idle_base": 2.1, "fuel": 45.0
        },
        # EQX1005: High-Use (48.0h engine, 2.4h idle -> 95.0% utilization, heavy fuel consumption)
        "EQX1005": {
            "lat": 37.8052, "lng": -122.2708,
            "engine_base": 48.0, "idle_base": 2.4, "fuel": 32.0
        },
        # EQX1006: Overdue Scissor Lift (22.0h engine, 3.5h idle)
        "EQX1006": {
            "lat": 37.7602, "lng": -122.4468,
            "engine_base": 22.0, "idle_base": 3.5, "fuel": 74.0
        },
        # EQX1007: Unassigned Yard Asset (0.0 active hours in yard, 100% fuel)
        "EQX1007": {
            "lat": 37.7610, "lng": -122.4480,
            "engine_base": 0.0, "idle_base": 0.0, "fuel": 100.0
        },
    }

    for eq_id, profile in telemetry_profiles.items():
        for i in range(6):
            t_offset = timedelta(hours=(5 - i) * 4)
            t_timestamp = base_time - t_offset
            step_factor = (i + 1) / 6.0

            t_record = {
                "equipment_id": eq_id,
                "timestamp": t_timestamp,
                "latitude": round(profile["lat"] + (i * 0.0001), 6),
                "longitude": round(profile["lng"] + (i * 0.0001), 6),
                "engine_hours": round(profile["engine_base"] * step_factor, 1),
                "idle_hours": round(profile["idle_base"] * step_factor, 1),
                "fuel_pct": max(5.0, round(profile["fuel"] - (i * 2.5), 1)),
                "created_at": t_timestamp,
            }

            existing = (
                db.query(Telemetry)
                .filter(
                    Telemetry.equipment_id == eq_id,
                    Telemetry.timestamp == t_timestamp,
                )
                .first()
            )
            if not existing:
                db.add(Telemetry(**t_record))

    db.flush()

    # 6. Seed Initial Alerts
    alerts_data = [
        {
            "equipment_id": "EQX1001",
            "alert_type": "LOW_UTILIZATION",
            "severity": "HIGH",
            "message": "Equipment EQX1001 idle hours (14.2h) exceed acceptable operational threshold (>8h). Utilization rate is 11.2%.",
            "status": "OPEN",
            "metadata_json": {"idle_hours": 14.2, "utilization_rate": 0.112, "threshold": 0.20},
            "created_at": base_time - timedelta(hours=8),
        },
        {
            "equipment_id": "EQX1002",
            "alert_type": "MISSING_ASSIGNMENT",
            "severity": "CRITICAL",
            "message": "Equipment EQX1002 is checked out at Northside Logistics Hub without an assigned certified operator.",
            "status": "OPEN",
            "metadata_json": {"site_id": "SITE-002", "missing_field": "operator_id"},
            "created_at": base_time - timedelta(hours=12),
        },
        {
            "equipment_id": "EQX1004",
            "alert_type": "DUE_SOON",
            "severity": "MEDIUM",
            "message": "Rental for Generator EQX1004 expires within 24 hours. Prepare return handoff or extension.",
            "status": "OPEN",
            "metadata_json": {"hours_remaining": 20, "site_id": "SITE-002"},
            "created_at": base_time - timedelta(hours=4),
        },
        {
            "equipment_id": "EQX1006",
            "alert_type": "OVERDUE",
            "severity": "HIGH",
            "message": "Rental for Scissor Lift EQX1006 is 48 hours overdue. Daily rate surcharge active ($180/day).",
            "status": "OPEN",
            "metadata_json": {"overdue_hours": 48, "daily_rate": 180.0},
            "created_at": base_time - timedelta(days=2),
        },
    ]

    for a_data in alerts_data:
        existing = (
            db.query(Alert)
            .filter(
                Alert.equipment_id == a_data["equipment_id"],
                Alert.alert_type == a_data["alert_type"],
                Alert.created_at == a_data["created_at"],
            )
            .first()
        )
        if not existing:
            db.add(Alert(**a_data))

    db.flush()

    # 7. Seed Initial Audit Events
    audit_events_data = [
        {
            "event_type": "CHECKOUT",
            "equipment_id": "EQX1001",
            "actor": "System Dispatch",
            "timestamp": base_time - timedelta(days=5),
            "metadata_json": {"site_id": "SITE-001", "operator_id": "OP-001", "daily_rate": 450.0},
        },
        {
            "event_type": "CHECKOUT",
            "equipment_id": "EQX1002",
            "actor": "Yard Logistics",
            "timestamp": base_time - timedelta(days=2),
            "metadata_json": {"site_id": "SITE-002", "operator_id": None, "daily_rate": 650.0},
        },
        {
            "event_type": "ALERT_CREATED",
            "equipment_id": "EQX1001",
            "actor": "Status Engine",
            "timestamp": base_time - timedelta(hours=8),
            "metadata_json": {"alert_type": "LOW_UTILIZATION", "idle_hours": 14.2},
        },
        {
            "event_type": "CHECKIN",
            "equipment_id": "EQX1007",
            "actor": "Marcus Vance",
            "timestamp": base_time - timedelta(days=3),
            "metadata_json": {"condition": "Returned clean, full tank", "site_id": "SITE-003"},
        },
    ]

    for ae_data in audit_events_data:
        existing = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.equipment_id == ae_data["equipment_id"],
                AuditEvent.event_type == ae_data["event_type"],
                AuditEvent.timestamp == ae_data["timestamp"],
            )
            .first()
        )
        if not existing:
            db.add(AuditEvent(**ae_data))

    db.commit()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db, reset=True)
    finally:
        db.close()
