from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    rentals = relationship("Rental", back_populates="operator")
