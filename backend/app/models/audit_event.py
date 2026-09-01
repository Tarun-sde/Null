from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    equipment_id = Column(String(50), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=True, index=True)
    actor = Column(String(100), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    equipment = relationship("Equipment", back_populates="audit_events")
