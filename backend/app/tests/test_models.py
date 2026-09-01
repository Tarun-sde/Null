from datetime import datetime, timezone
from app.db.session import SessionLocal, Base, engine
from app.models import (
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


def test_all_models_instantiation():
    db = SessionLocal()
    try:
        # Create a test site
        site = Site(
            id="TEST-SITE-1",
            name="Test Construction Site",
            location="Zone A",
            latitude=37.77,
            longitude=-122.41,
        )
        db.add(site)

        # Create a test operator
        operator = Operator(
            id="TEST-OP-1",
            name="Test Operator",
            contact="op@test.com",
        )
        db.add(operator)

        # Create test equipment
        equipment = Equipment(
            id="TEST-EQ-1",
            type="Excavator",
            dealer="Test Dealer",
            daily_rate=500.0,
            metadata_json={"model": "Test Model"},
        )
        db.add(equipment)
        db.flush()

        # Create test rental
        rental = Rental(
            equipment_id="TEST-EQ-1",
            site_id="TEST-SITE-1",
            operator_id="TEST-OP-1",
            daily_rate=500.0,
        )
        db.add(rental)

        # Create test telemetry
        telemetry = Telemetry(
            equipment_id="TEST-EQ-1",
            timestamp=datetime.now(timezone.utc),
            latitude=37.77,
            longitude=-122.41,
            engine_hours=10.0,
            idle_hours=2.0,
            fuel_pct=90.0,
        )
        db.add(telemetry)

        # Create test alert
        alert = Alert(
            equipment_id="TEST-EQ-1",
            alert_type="TEST_ALERT",
            severity="LOW",
            message="Test message",
        )
        db.add(alert)

        # Create test forecast
        forecast = Forecast(
            site_id="TEST-SITE-1",
            equipment_type="Excavator",
            forecast_date=datetime.now(timezone.utc),
            predicted_units=2.0,
            confidence=0.9,
        )
        db.add(forecast)

        # Create test recommendation
        recommendation = Recommendation(
            equipment_id="TEST-EQ-1",
            recommendation_type="RETURN",
            priority="HIGH",
            explanation="Test explanation",
            action="Return to depot",
        )
        db.add(recommendation)

        # Create test audit event
        audit_event = AuditEvent(
            event_type="CHECKOUT",
            equipment_id="TEST-EQ-1",
            actor="Test Actor",
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit_event)

        db.commit()

        # Query and verify relationships
        saved_eq = db.query(Equipment).filter(Equipment.id == "TEST-EQ-1").first()
        assert saved_eq is not None
        assert len(saved_eq.rentals) == 1
        assert len(saved_eq.telemetry) == 1
        assert len(saved_eq.alerts) == 1
        assert len(saved_eq.recommendations) == 1
        assert len(saved_eq.audit_events) == 1

        # Clean up test records
        db.delete(saved_eq)
        db.delete(site)
        db.delete(operator)
        db.commit()
    finally:
        db.close()
