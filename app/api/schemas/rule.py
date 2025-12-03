"""Pydantic schemas for monitoring rules."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.models.rule import PatternType


class MonitoringRuleBase(BaseModel):
    """Base monitoring rule schema."""
    name: str
    description: Optional[str] = None
    enabled: bool = True
    log_type: str
    pattern_type: PatternType
    pattern_value: str
    threshold_count: Optional[int] = None
    threshold_window_minutes: Optional[int] = None


class MonitoringRuleCreate(MonitoringRuleBase):
    """Schema for creating a monitoring rule."""
    pass


class MonitoringRuleUpdate(BaseModel):
    """Schema for updating a monitoring rule."""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    log_type: Optional[str] = None
    pattern_type: Optional[PatternType] = None
    pattern_value: Optional[str] = None
    threshold_count: Optional[int] = None
    threshold_window_minutes: Optional[int] = None


class MonitoringRuleResponse(MonitoringRuleBase):
    """Schema for monitoring rule response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MonitoringRuleListResponse(BaseModel):
    """Schema for monitoring rule list."""
    rules: list[MonitoringRuleResponse]
    total: int
