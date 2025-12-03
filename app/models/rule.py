"""Monitoring rule model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class PatternType(str, enum.Enum):
    """Enum for pattern matching types."""

    ERROR_CODE = "error_code"
    REGEX = "regex"
    STATUS = "status"
    THRESHOLD = "threshold"


class MonitoringRule(Base):
    """Model for monitoring rules."""

    __tablename__ = "monitoring_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    log_type = Column(String(50), nullable=False)  # Using String to allow flexibility
    pattern_type = Column(SQLEnum(PatternType), nullable=False)
    pattern_value = Column(Text, nullable=False)
    threshold_count = Column(Integer, nullable=True)
    threshold_window_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    actions = relationship(
        "Action", back_populates="rule", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<MonitoringRule(id={self.id}, name={self.name}, enabled={self.enabled})>"
        )
