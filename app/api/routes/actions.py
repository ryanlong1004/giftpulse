"""Action API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Action, AlertHistory
from app.api.schemas.action import (
    ActionCreate,
    ActionUpdate,
    ActionResponse,
    ActionListResponse,
    AlertHistoryResponse,
    AlertHistoryListResponse
)

router = APIRouter()


@router.get("/actions", response_model=ActionListResponse)
def list_actions(db: Session = Depends(get_db)):
    """
    List all actions.
    
    Args:
        db: Database session
    
    Returns:
        List of actions
    """
    actions = db.query(Action).order_by(Action.created_at.desc()).all()
    
    return ActionListResponse(
        actions=actions,
        total=len(actions)
    )


@router.get("/actions/{action_id}", response_model=ActionResponse)
def get_action(
    action_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific action by ID.
    
    Args:
        action_id: Action UUID
        db: Database session
    
    Returns:
        Action details
    """
    action = db.query(Action).filter(Action.id == action_id).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return action


@router.post("/actions", response_model=ActionResponse, status_code=201)
def create_action(
    action_data: ActionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new action.
    
    Args:
        action_data: Action creation data
        db: Database session
    
    Returns:
        Created action
    """
    action = Action(**action_data.model_dump())
    
    db.add(action)
    db.commit()
    db.refresh(action)
    
    return action


@router.put("/actions/{action_id}", response_model=ActionResponse)
def update_action(
    action_id: UUID,
    action_data: ActionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an action.
    
    Args:
        action_id: Action UUID
        action_data: Action update data
        db: Database session
    
    Returns:
        Updated action
    """
    action = db.query(Action).filter(Action.id == action_id).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Update fields
    update_data = action_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(action, field, value)
    
    db.commit()
    db.refresh(action)
    
    return action


@router.delete("/actions/{action_id}", status_code=204)
def delete_action(
    action_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an action.
    
    Args:
        action_id: Action UUID
        db: Database session
    """
    action = db.query(Action).filter(Action.id == action_id).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    db.delete(action)
    db.commit()
    
    return None


@router.get("/alerts", response_model=AlertHistoryListResponse)
def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List alert history with pagination.
    
    Args:
        page: Page number
        page_size: Items per page
        db: Database session
    
    Returns:
        Paginated alert history
    """
    query = db.query(AlertHistory)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    alerts = query.order_by(
        AlertHistory.triggered_at.desc()
    ).offset(offset).limit(page_size).all()
    
    return AlertHistoryListResponse(
        alerts=alerts,
        total=total,
        page=page,
        page_size=page_size
    )
