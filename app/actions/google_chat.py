"""Google Chat action handler."""

import httpx
from typing import Dict, Any

from app.actions.base import BaseActionHandler
from app.models import Log
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleChatActionHandler(BaseActionHandler):
    """Handler for sending Google Chat notifications."""

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Google Chat configuration.

        Args:
            config: Configuration with 'webhook_url'

        Returns:
            True if valid
        """
        if "webhook_url" not in config:
            logger.error("Google Chat config missing 'webhook_url'")
            return False

        return True

    def _format_message(self, log: Log, config: Dict[str, Any]) -> str:
        """
        Format message for Google Chat.

        Args:
            log: Log data
            config: Action configuration

        Returns:
            Formatted message text
        """
        template = config.get("template")

        if template:
            # Use custom template if provided
            return template.format(
                log_type=log.log_type.value,
                status=log.status,
                error_code=log.error_code or "N/A",
                error_message=log.error_message or "N/A",
                from_number=log.from_number or "N/A",
                to_number=log.to_number or "N/A",
                timestamp=log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                twilio_sid=log.twilio_sid,
            )

        # Default format
        emoji = "🚨" if log.error_code else "ℹ️"

        message = f"{emoji} *Twilio {log.log_type.value.title()} Alert*\n\n"

        if log.error_code:
            message += f"• Error Code: {log.error_code}\n"
        if log.error_message:
            message += f"• Message: {log.error_message}\n"
        if log.status:
            message += f"• Status: {log.status}\n"
        if log.from_number:
            message += f"• From: {log.from_number}\n"
        if log.to_number:
            message += f"• To: {log.to_number}\n"

        message += f"• Time: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"• SID: `{log.twilio_sid}`"

        return message

    def execute(self, config: Dict[str, Any], log: Log) -> Dict[str, Any]:
        """
        Execute Google Chat notification.

        Args:
            config: Action configuration with webhook_url
            log: Log that triggered the action

        Returns:
            Execution result
        """
        if not self.validate_config(config):
            return {"success": False, "error": "Invalid configuration"}

        webhook_url = config["webhook_url"]
        message_text = self._format_message(log, config)

        # Create Google Chat message payload
        payload = {"text": message_text}

        # Add card format if specified
        if config.get("use_card", False):
            payload = {
                "cards": [
                    {
                        "header": {
                            "title": f"Twilio {log.log_type.value.title()} Alert",
                            "subtitle": log.status or "Status Unknown",
                        },
                        "sections": [
                            {"widgets": [{"textParagraph": {"text": message_text}}]}
                        ],
                    }
                ]
            }

        try:
            logger.info(f"Sending Google Chat message to webhook")

            with httpx.Client(timeout=settings.webhook_timeout_seconds) as client:
                response = client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()

            logger.info(
                f"Google Chat message sent successfully: {response.status_code}"
            )

            return {
                "success": True,
                "status_code": response.status_code,
                "webhook_url": webhook_url,
            }

        except httpx.HTTPError as e:
            logger.error(f"Error sending Google Chat message: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
