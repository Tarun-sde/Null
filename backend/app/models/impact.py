from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class ImpactRecord(Base):
    __tablename__ = "impact_records"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id", ondelete="CASCADE"), nullable=True, index=True)
    equipment_id = Column(String(50), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(String(50), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    impact_type = Column(String(100), nullable=False, index=True)  # IDLE_AVOIDANCE, EARLY_RETURN, OVERDUE_SURCHARGE_AVOIDED, UTILIZATION_RECOVERY
    estimated_amount = Column(Float, nullable=False, default=0.0)
    realized_amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default="USD")
    calculation_basis = Column(Text, nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    action = relationship("Action", back_populates="impact_record")
    equipment = relationship("Equipment")
    site = relationship("Site")
