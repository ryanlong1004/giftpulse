"""Twilio API client wrapper."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwilioClientWrapper:
    """Wrapper for Twilio API client with error handling and retry logic."""

    def __init__(
        self, account_sid: Optional[str] = None, auth_token: Optional[str] = None
    ):
        """
        Initialize Twilio client.

        Args:
            account_sid: Twilio Account SID (defaults to settings)
            auth_token: Twilio Auth Token (defaults to settings)
        """
        self.account_sid = account_sid or settings.twilio_account_sid
        self.auth_token = auth_token or settings.twilio_auth_token
        self.client = Client(self.account_sid, self.auth_token)
        logger.info("Twilio client initialized")

    def fetch_call_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch call logs from Twilio.

        Args:
            start_date: Start date for log query
            end_date: End date for log query
            limit: Maximum number of logs to fetch

        Returns:
            List of call log dictionaries
        """
        try:
            logger.info(
                f"Fetching call logs: start={start_date}, end={end_date}, limit={limit}"
            )

            calls = self.client.calls.list(
                start_time_after=start_date, start_time_before=end_date, limit=limit
            )

            logs = []
            for call in calls:
                log_data = {
                    "sid": call.sid,
                    "from": call.from_,
                    "to": call.to,
                    "status": call.status,
                    "duration": call.duration,
                    "start_time": call.start_time,
                    "end_time": call.end_time,
                    "price": call.price,
                    "price_unit": call.price_unit,
                    "direction": call.direction,
                    "error_code": getattr(call, "error_code", None),
                    "error_message": getattr(call, "error_message", None),
                }
                logs.append(log_data)

            logger.info(f"Fetched {len(logs)} call logs")
            return logs

        except TwilioRestException as e:
            logger.error(f"Twilio API error fetching calls: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching calls: {e}")
            raise

    def fetch_message_logs(
        self,
        date_sent_after: Optional[datetime] = None,
        date_sent_before: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch message logs from Twilio.

        Args:
            date_sent_after: Start date for log query
            date_sent_before: End date for log query
            limit: Maximum number of logs to fetch

        Returns:
            List of message log dictionaries
        """
        try:
            logger.info(
                f"Fetching message logs: after={date_sent_after}, "
                f"before={date_sent_before}, limit={limit}"
            )

            messages = self.client.messages.list(
                date_sent_after=date_sent_after,
                date_sent_before=date_sent_before,
                limit=limit,
            )

            logs = []
            for message in messages:
                log_data = {
                    "sid": message.sid,
                    "from": message.from_,
                    "to": message.to,
                    "body": message.body,
                    "status": message.status,
                    "direction": message.direction,
                    "date_sent": message.date_sent,
                    "date_created": message.date_created,
                    "price": message.price,
                    "price_unit": message.price_unit,
                    "error_code": message.error_code,
                    "error_message": message.error_message,
                    "num_segments": message.num_segments,
                }
                logs.append(log_data)

            logger.info(f"Fetched {len(logs)} message logs")
            return logs

        except TwilioRestException as e:
            logger.error(f"Twilio API error fetching messages: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching messages: {e}")
            raise

    def fetch_alerts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch alerts/warnings from Twilio Monitor.

        Args:
            start_date: Start date for alert query
            end_date: End date for alert query
            limit: Maximum number of alerts to fetch

        Returns:
            List of alert dictionaries
        """
        try:
            logger.info(
                f"Fetching alerts: start={start_date}, end={end_date}, limit={limit}"
            )

            # Build parameters
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if limit:
                params["limit"] = limit

            alerts = self.client.monitor.v1.alerts.list(**params)

            logs = []
            for alert in alerts:
                log_data = {
                    "sid": alert.sid,
                    "alert_text": alert.alert_text,
                    "log_level": alert.log_level,
                    "date_created": alert.date_created,
                    "date_updated": alert.date_updated,
                    "error_code": alert.error_code,
                    "more_info": alert.more_info,
                    "request_method": alert.request_method,
                    "request_url": alert.request_url,
                    "service_sid": alert.service_sid,
                }
                logs.append(log_data)

            logger.info(f"Fetched {len(logs)} alerts")
            return logs

        except TwilioRestException as e:
            logger.error(f"Twilio API error fetching alerts: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching alerts: {e}")
            raise

    def fetch_recent_logs(
        self,
        minutes: int = 5,
        include_calls: bool = True,
        include_messages: bool = True,
        include_alerts: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch all recent logs from the last N minutes.

        Args:
            minutes: Number of minutes to look back
            include_calls: Include call logs
            include_messages: Include message logs
            include_alerts: Include alerts

        Returns:
            Dictionary with 'calls', 'messages', and 'alerts' lists
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)

        logger.info(f"Fetching recent logs from last {minutes} minutes")

        result = {"calls": [], "messages": [], "alerts": []}

        try:
            if include_calls:
                result["calls"] = self.fetch_call_logs(
                    start_date=start_time, end_date=end_time
                )

            if include_messages:
                result["messages"] = self.fetch_message_logs(
                    date_sent_after=start_time, date_sent_before=end_time
                )

            if include_alerts:
                result["alerts"] = self.fetch_alerts(
                    start_date=start_time, end_date=end_time
                )

            total = (
                len(result["calls"]) + len(result["messages"]) + len(result["alerts"])
            )
            logger.info(f"Fetched total of {total} recent logs")

            return result

        except Exception as e:
            logger.error(f"Error fetching recent logs: {e}")
            raise


# Singleton instance
_twilio_client: Optional[TwilioClientWrapper] = None


def get_twilio_client() -> TwilioClientWrapper:
    """
    Get singleton Twilio client instance.

    Returns:
        TwilioClientWrapper instance
    """
    global _twilio_client

    if _twilio_client is None:
        _twilio_client = TwilioClientWrapper()

    return _twilio_client
