"""Webhook action handler."""

import httpx
from typing import Dict, Any
import json

from app.actions.base import BaseActionHandler
from app.models import Log
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebhookActionHandler(BaseActionHandler):
    """Handler for triggering webhooks."""

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate webhook configuration.

        Args:
            config: Configuration with 'url'

        Returns:
            True if valid
        """
        if "url" not in config:
            logger.error("Webhook config missing 'url'")
            return False

        if not isinstance(config["url"], str):
            logger.error("Webhook 'url' must be a string")
            return False

        if not config["url"].startswith(("http://", "https://")):
            logger.error("Webhook 'url' must start with http:// or https://")
            return False

        return True

    def _create_payload(
        self, log: Log, custom_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create webhook payload.

        Args:
            log: Log data
            custom_data: Additional custom data or complete payload override

        Returns:
            Payload dictionary
        """
        # If custom_data is provided, use it as the complete payload
        if custom_data:
            return custom_data

        # Default payload with log data
        payload = {
            "log_id": str(log.id),
            "twilio_sid": log.twilio_sid,
            "log_type": log.log_type.value,
            "timestamp": log.timestamp.isoformat(),
            "status": log.status,
            "error_code": log.error_code,
            "error_message": log.error_message,
            "from_number": log.from_number,
            "to_number": log.to_number,
        }

        return payload

    def execute(self, config: Dict[str, Any], log: Log) -> Dict[str, Any]:
        """
        Trigger webhook.

        Args:
            config: Webhook configuration
            log: Log that triggered the action

        Returns:
            Execution result
        """
        if not self.validate_config(config):
            return {"success": False, "error": "Invalid configuration"}

        url = config["url"]
        method = config.get("method", "POST").upper()
        headers = config.get("headers", {})
        custom_data = config.get("data", {})

        # Ensure Content-Type is set
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        # Create payload
        payload = self._create_payload(log, custom_data)

        # Retry logic
        max_retries = settings.webhook_retry_attempts
        timeout = settings.webhook_timeout_seconds

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Sending webhook to {url} (attempt {attempt + 1}/{max_retries})"
                )

                with httpx.Client(timeout=timeout) as client:
                    if method == "POST":
                        response = client.post(url, json=payload, headers=headers)
                    elif method == "PUT":
                        response = client.put(url, json=payload, headers=headers)
                    else:
                        return {
                            "success": False,
                            "error": f"Unsupported HTTP method: {method}",
                        }

                    response.raise_for_status()

                logger.info(f"Webhook sent successfully: {response.status_code}")

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response.text[:500],  # Truncate response
                    "url": url,
                    "attempts": attempt + 1,
                }

            except httpx.HTTPError as e:
                logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")

                if attempt == max_retries - 1:
                    # Last attempt failed
                    logger.error(f"Webhook failed after {max_retries} attempts")
                    return {
                        "success": False,
                        "error": str(e),
                        "url": url,
                        "attempts": attempt + 1,
                    }

                # Wait before retry
                import time

                time.sleep(settings.webhook_retry_delay_seconds)

            except Exception as e:
                logger.error(f"Unexpected error sending webhook: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "url": url,
                    "attempts": attempt + 1,
                }

        return {"success": False, "error": "Unknown error", "url": url}
