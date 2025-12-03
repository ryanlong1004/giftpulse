"""Monitoring rule API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import MonitoringRule
from app.api.schemas.rule import (
    MonitoringRuleCreate,
    MonitoringRuleUpdate,
    MonitoringRuleResponse,
    MonitoringRuleListResponse
)

router = APIRouter()


@router.get("/rules", response_model=MonitoringRuleListResponse)
def list_rules(db: Session = Depends(get_db)):
    """
    List all monitoring rules.
    
    Args:
        db: Database session
    
    Returns:
        List of monitoring rules
    """
    rules = db.query(MonitoringRule).order_by(MonitoringRule.created_at.desc()).all()
    
    return MonitoringRuleListResponse(
        rules=rules,
        total=len(rules)
    )


@router.get("/rules/{rule_id}", response_model=MonitoringRuleResponse)
def get_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific monitoring rule by ID.
    
    Args:
        rule_id: Rule UUID
        db: Database session
    
    Returns:
        Rule details
    """
    rule = db.query(MonitoringRule).filter(MonitoringRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return rule


@router.post("/rules", response_model=MonitoringRuleResponse, status_code=201)
def create_rule(
    rule_data: MonitoringRuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new monitoring rule.
    
    Args:
        rule_data: Rule creation data
        db: Database session
    
    Returns:
        Created rule
    """
    rule = MonitoringRule(**rule_data.model_dump())
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.put("/rules/{rule_id}", response_model=MonitoringRuleResponse)
def update_rule(
    rule_id: UUID,
    rule_data: MonitoringRuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a monitoring rule.
    
    Args:
        rule_id: Rule UUID
        rule_data: Rule update data
        db: Database session
    
    Returns:
        Updated rule
    """
    rule = db.query(MonitoringRule).filter(MonitoringRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update fields
    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    return rule


@router.delete("/rules/{rule_id}", status_code=204)
def delete_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a monitoring rule.
    
    Args:
        rule_id: Rule UUID
        db: Database session
    """
    rule = db.query(MonitoringRule).filter(MonitoringRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    
    return None
