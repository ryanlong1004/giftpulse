"""Log API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Log
from app.api.schemas.log import LogResponse, LogListResponse

router = APIRouter()


@router.get("/logs", response_model=LogListResponse)
def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    log_type: Optional[str] = None,
    processed: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    List logs with pagination and filtering.

    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page
        log_type: Filter by log type
        processed: Filter by processed status
        db: Database session

    Returns:
        Paginated list of logs
    """
    query = db.query(Log)

    # Apply filters
    if log_type:
        query = query.filter(Log.log_type == log_type)

    if processed is not None:
        query = query.filter(Log.processed == processed)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    logs = query.order_by(Log.timestamp.desc()).offset(offset).limit(page_size).all()

    return LogListResponse(logs=logs, total=total, page=page, page_size=page_size)


@router.get("/logs/{log_id}", response_model=LogResponse)
def get_log(log_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific log by ID.

    Args:
        log_id: Log UUID
        db: Database session

    Returns:
        Log details
    """
    from fastapi import HTTPException

    log = db.query(Log).filter(Log.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    return log
