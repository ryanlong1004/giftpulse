"""Pydantic schemas for actions."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.models.action import ActionType


class ActionBase(BaseModel):
    """Base action schema."""
    action_type: ActionType
    config: dict
    enabled: bool = True


class ActionCreate(ActionBase):
    """Schema for creating an action."""
    rule_id: UUID


class ActionUpdate(BaseModel):
    """Schema for updating an action."""
    action_type: Optional[ActionType] = None
    config: Optional[dict] = None
    enabled: Optional[bool] = None


class ActionResponse(ActionBase):
    """Schema for action response."""
    id: UUID
    rule_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ActionListResponse(BaseModel):
    """Schema for action list."""
    actions: list[ActionResponse]
    total: int


class AlertHistoryResponse(BaseModel):
    """Schema for alert history response."""
    id: UUID
    rule_id: UUID
    log_id: UUID
    action_id: UUID
    triggered_at: datetime
    action_result: Optional[dict] = None
    success: bool
    
    model_config = ConfigDict(from_attributes=True)


class AlertHistoryListResponse(BaseModel):
    """Schema for alert history list."""
    alerts: list[AlertHistoryResponse]
    total: int
    page: int
    page_size: int
