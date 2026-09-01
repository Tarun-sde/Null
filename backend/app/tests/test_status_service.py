from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from app.services.status_service import derive_status, calculate_utilization, EquipmentStatus


def test_calculate_utilization():
    assert calculate_utilization(0, 0) == 0.0
    assert calculate_utilization(10.0, 5.0) == 0.5
    assert calculate_utilization(16.0, 14.0) == 0.125
    assert calculate_utilization(48.0, 2.4) == 0.95


def test_status_unassigned_no_rental():
    # No rental object
    assert derive_status(rental=None, telemetry=None) == EquipmentStatus.UNASSIGNED


def test_status_unassigned_closed_rental():
    # Rental already checked in
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id="OP-001",
        checked_in_at=now - timedelta(days=1),
        due_at=now + timedelta(days=5),
    )
    assert derive_status(rental=rental, telemetry=None, now=now) == EquipmentStatus.UNASSIGNED


def test_status_unassigned_missing_operator():
    # Rental active but missing operator assignment
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id=None,
        checked_in_at=None,
        due_at=now + timedelta(days=5),
    )
    assert derive_status(rental=rental, telemetry=None, now=now) == EquipmentStatus.UNASSIGNED


def test_status_unassigned_missing_site():
    # Rental active but missing site assignment
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id=None,
        operator_id="OP-001",
        checked_in_at=None,
        due_at=now + timedelta(days=5),
    )
    assert derive_status(rental=rental, telemetry=None, now=now) == EquipmentStatus.UNASSIGNED


def test_status_overdue():
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id="OP-001",
        checked_in_at=None,
        due_at=now - timedelta(hours=2),  # Overdue by 2 hours
    )
    assert derive_status(rental=rental, telemetry=None, now=now) == EquipmentStatus.OVERDUE


def test_status_due_soon():
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id="OP-001",
        checked_in_at=None,
        due_at=now + timedelta(hours=24),  # Due in 24h (<48h threshold)
    )
    assert derive_status(rental=rental, telemetry=None, now=now) == EquipmentStatus.DUE_SOON


def test_status_idle_by_idle_hours():
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id="OP-001",
        checked_in_at=None,
        due_at=now + timedelta(days=5),
    )
    telemetry = SimpleNamespace(
        engine_hours=20.0,
        idle_hours=10.0,  # >= 8.0h threshold
    )
    assert derive_status(rental=rental, telemetry=telemetry, now=now) == EquipmentStatus.IDLE


def test_status_idle_by_low_utilization():
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id="OP-001",
        checked_in_at=None,
        due_at=now + timedelta(days=5),
    )
    telemetry = SimpleNamespace(
        engine_hours=7.0,  # Below 8h idle, but utilization = 1/7 = 14.3% < 20%
        idle_hours=6.0,
    )
    assert derive_status(rental=rental, telemetry=telemetry, now=now) == EquipmentStatus.IDLE


def test_status_active_normal():
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id="OP-001",
        checked_in_at=None,
        due_at=now + timedelta(days=5),
    )
    telemetry = SimpleNamespace(
        engine_hours=30.0,
        idle_hours=4.0,  # Utilization = 26/30 = 86.7% > 20% and idle < 8h
    )
    assert derive_status(rental=rental, telemetry=telemetry, now=now) == EquipmentStatus.ACTIVE


def test_status_precedence_overdue_over_idle():
    # If equipment is overdue AND idle, overdue takes precedence
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    rental = SimpleNamespace(
        site_id="SITE-001",
        operator_id="OP-001",
        checked_in_at=None,
        due_at=now - timedelta(days=1),  # Overdue
    )
    telemetry = SimpleNamespace(
        engine_hours=20.0,
        idle_hours=15.0,  # Also idle
    )
    assert derive_status(rental=rental, telemetry=telemetry, now=now) == EquipmentStatus.OVERDUE
