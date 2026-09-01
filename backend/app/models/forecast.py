from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    site_id = Column(String(50), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    equipment_type = Column(String(100), nullable=False, index=True)
    forecast_date = Column(DateTime(timezone=True), nullable=False, index=True)
    predicted_units = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=0.85)
    backtest_error = Column(Float, nullable=True)
    drivers = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    site = relationship("Site", back_populates="forecasts")
