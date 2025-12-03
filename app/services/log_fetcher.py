"""Log fetching service."""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database import get_db_context
from app.models import Log, LogType
from app.services.twilio_client import get_twilio_client
from app.utils.logger import get_logger
from app.utils.helpers import sanitize_phone_number

logger = get_logger(__name__)


class LogFetcherService:
    """Service for fetching and storing Twilio logs."""
    
    def __init__(self):
        """Initialize log fetcher service."""
        self.twilio_client = get_twilio_client()
    
    def _log_exists(self, db: Session, twilio_sid: str) -> bool:
        """
        Check if log already exists in database.
        
        Args:
            db: Database session
            twilio_sid: Twilio SID to check
        
        Returns:
            True if log exists
        """
        return db.query(Log).filter(Log.twilio_sid == twilio_sid).first() is not None
    
    def _save_call_logs(
        self,
        db: Session,
        call_logs: List[Dict[str, Any]]
    ) -> int:
        """
        Save call logs to database.
        
        Args:
            db: Database session
            call_logs: List of call log dictionaries
        
        Returns:
            Number of new logs saved
        """
        saved_count = 0
        
        for log_data in call_logs:
            sid = log_data.get('sid')
            
            # Skip if already exists
            if self._log_exists(db, sid):
                continue
            
            # Create log entry
            log = Log(
                twilio_sid=sid,
                log_type=LogType.CALL,
                timestamp=log_data.get('start_time') or datetime.utcnow(),
                status=log_data.get('status'),
                error_code=log_data.get('error_code'),
                error_message=log_data.get('error_message'),
                from_number=sanitize_phone_number(log_data.get('from')),
                to_number=sanitize_phone_number(log_data.get('to')),
                raw_data=log_data,
                processed=False
            )
            
            db.add(log)
            saved_count += 1
        
        db.commit()
        return saved_count
    
    def _save_message_logs(
        self,
        db: Session,
        message_logs: List[Dict[str, Any]]
    ) -> int:
        """
        Save message logs to database.
        
        Args:
            db: Database session
            message_logs: List of message log dictionaries
        
        Returns:
            Number of new logs saved
        """
        saved_count = 0
        
        for log_data in message_logs:
            sid = log_data.get('sid')
            
            # Skip if already exists
            if self._log_exists(db, sid):
                continue
            
            # Create log entry
            log = Log(
                twilio_sid=sid,
                log_type=LogType.MESSAGE,
                timestamp=log_data.get('date_sent') or datetime.utcnow(),
                status=log_data.get('status'),
                error_code=str(log_data.get('error_code')) if log_data.get('error_code') else None,
                error_message=log_data.get('error_message'),
                from_number=sanitize_phone_number(log_data.get('from')),
                to_number=sanitize_phone_number(log_data.get('to')),
                raw_data=log_data,
                processed=False
            )
            
            db.add(log)
            saved_count += 1
        
        db.commit()
        return saved_count
    
    def _save_alert_logs(
        self,
        db: Session,
        alert_logs: List[Dict[str, Any]]
    ) -> int:
        """
        Save alert logs to database.
        
        Args:
            db: Database session
            alert_logs: List of alert log dictionaries
        
        Returns:
            Number of new logs saved
        """
        saved_count = 0
        
        for log_data in alert_logs:
            sid = log_data.get('sid')
            
            # Skip if already exists
            if self._log_exists(db, sid):
                continue
            
            # Determine log type based on level
            log_level = log_data.get('log_level', '').lower()
            if log_level == 'error':
                log_type = LogType.ERROR
            elif log_level == 'warning':
                log_type = LogType.WARNING
            else:
                log_type = LogType.DEBUG
            
            # Create log entry
            log = Log(
                twilio_sid=sid,
                log_type=log_type,
                timestamp=log_data.get('date_created') or datetime.utcnow(),
                status=None,
                error_code=log_data.get('error_code'),
                error_message=log_data.get('alert_text'),
                from_number=None,
                to_number=None,
                raw_data=log_data,
                processed=False
            )
            
            db.add(log)
            saved_count += 1
        
        db.commit()
        return saved_count
    
    def fetch_and_store_recent_logs(
        self,
        minutes: int = 5
    ) -> Dict[str, int]:
        """
        Fetch recent logs from Twilio and store in database.
        
        Args:
            minutes: Number of minutes to look back
        
        Returns:
            Dictionary with counts of saved logs by type
        """
        logger.info(f"Fetching logs from last {minutes} minutes")
        
        try:
            # Fetch logs from Twilio
            logs = self.twilio_client.fetch_recent_logs(minutes=minutes)
            
            # Save to database
            with get_db_context() as db:
                call_count = self._save_call_logs(db, logs['calls'])
                message_count = self._save_message_logs(db, logs['messages'])
                alert_count = self._save_alert_logs(db, logs['alerts'])
            
            result = {
                'calls': call_count,
                'messages': message_count,
                'alerts': alert_count,
                'total': call_count + message_count + alert_count
            }
            
            logger.info(
                f"Saved {result['total']} new logs: "
                f"{call_count} calls, {message_count} messages, "
                f"{alert_count} alerts"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching and storing logs: {e}")
            raise


# Singleton instance
_log_fetcher: Optional[LogFetcherService] = None


def get_log_fetcher() -> LogFetcherService:
    """
    Get singleton log fetcher instance.
    
    Returns:
        LogFetcherService instance
    """
    global _log_fetcher
    
    if _log_fetcher is None:
        _log_fetcher = LogFetcherService()
    
    return _log_fetcher
