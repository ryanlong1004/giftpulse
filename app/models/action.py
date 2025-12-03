"""Action model for monitoring rule actions."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ActionType(str, enum.Enum):
    """Enum for action types."""

    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"


class Action(Base):
    """Model for actions triggered by monitoring rules."""

    __tablename__ = "actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("monitoring_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type = Column(SQLEnum(ActionType), nullable=False)
    config = Column(JSONB, nullable=False)  # Stores email addresses, webhook URLs, etc.
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    rule = relationship("MonitoringRule", back_populates="actions")
    alert_history = relationship("AlertHistory", back_populates="action")

    def __repr__(self):
        return (
            f"<Action(id={self.id}, type={self.action_type}, rule_id={self.rule_id})>"
        )
