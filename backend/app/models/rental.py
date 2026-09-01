from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    equipment_id = Column(String(50), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(String(50), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    operator_id = Column(String(50), ForeignKey("operators.id", ondelete="SET NULL"), nullable=True, index=True)
    checked_out_at = Column(DateTime(timezone=True), nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True, index=True)
    checked_in_at = Column(DateTime(timezone=True), nullable=True, index=True)
    daily_rate = Column(Float, nullable=False)
    condition_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    equipment = relationship("Equipment", back_populates="rentals")
    site = relationship("Site", back_populates="rentals")
    operator = relationship("Operator", back_populates="rentals")
