from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    equipment_id = Column(String(50), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_type = Column(String(100), nullable=False, index=True)
    priority = Column(String(50), nullable=False, default="MEDIUM", index=True)
    explanation = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.9)
    estimated_impact = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    equipment = relationship("Equipment", back_populates="recommendations")
