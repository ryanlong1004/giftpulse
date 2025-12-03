"""Pydantic schemas for logs."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.models.log import LogType


class LogBase(BaseModel):
    """Base log schema."""
    log_type: LogType
    timestamp: datetime
    status: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    from_number: Optional[str] = None
    to_number: Optional[str] = None


class LogCreate(LogBase):
    """Schema for creating a log."""
    twilio_sid: str
    raw_data: dict


class LogResponse(LogBase):
    """Schema for log response."""
    id: UUID
    twilio_sid: str
    processed: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LogListResponse(BaseModel):
    """Schema for paginated log list."""
    logs: list[LogResponse]
    total: int
    page: int
    page_size: int
