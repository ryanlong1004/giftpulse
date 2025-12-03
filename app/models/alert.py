"""Alert history model for tracking triggered alerts."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class AlertHistory(Base):
    """Model for tracking alert history."""

    __tablename__ = "alert_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("monitoring_rules.id"),
        nullable=False,
        index=True,
    )
    log_id = Column(
        UUID(as_uuid=True), ForeignKey("logs.id"), nullable=False, index=True
    )
    action_id = Column(
        UUID(as_uuid=True), ForeignKey("actions.id"), nullable=False, index=True
    )
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    action_result = Column(JSONB, nullable=True)  # Stores action execution results
    success = Column(Boolean, nullable=False, index=True)

    # Relationships
    action = relationship("Action", back_populates="alert_history")

    def __repr__(self):
        return f"<AlertHistory(id={self.id}, rule_id={self.rule_id}, success={self.success})>"
