"""Log model for storing Twilio logs."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from app.database import Base


class LogType(str, enum.Enum):
    """Enum for log types."""

    CALL = "call"
    MESSAGE = "message"
    ERROR = "error"
    WARNING = "warning"
    DEBUG = "debug"


class Log(Base):
    """Model for storing Twilio logs."""

    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    twilio_sid = Column(String(255), unique=True, nullable=False, index=True)
    log_type = Column(SQLEnum(LogType), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), nullable=True, index=True)
    error_code = Column(String(50), nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    from_number = Column(String(50), nullable=True)
    to_number = Column(String(50), nullable=True)
    raw_data = Column(JSONB, nullable=False)
    processed = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Log(id={self.id}, type={self.log_type}, sid={self.twilio_sid})>"
