from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String(50), primary_key=True, index=True)
    type = Column(String(100), nullable=False, index=True)
    dealer = Column(String(100), nullable=False)
    daily_rate = Column(Float, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    rentals = relationship("Rental", back_populates="equipment", cascade="all, delete-orphan", order_by="desc(Rental.created_at)")
    telemetry = relationship("Telemetry", back_populates="equipment", cascade="all, delete-orphan", order_by="desc(Telemetry.timestamp)")
    alerts = relationship("Alert", back_populates="equipment", cascade="all, delete-orphan", order_by="desc(Alert.created_at)")
    recommendations = relationship("Recommendation", back_populates="equipment", cascade="all, delete-orphan", order_by="desc(Recommendation.created_at)")
    audit_events = relationship("AuditEvent", back_populates="equipment", cascade="all, delete-orphan", order_by="desc(AuditEvent.timestamp)")
