"""Action handler service for executing actions."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models import Action, ActionType, Log, AlertHistory
from app.actions.email import EmailActionHandler
from app.actions.webhook import WebhookActionHandler
from app.actions.google_chat import GoogleChatActionHandler
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ActionHandlerService:
    """Service for executing actions triggered by monitoring rules."""

    def __init__(self):
        """Initialize action handlers."""
        self.handlers = {
            ActionType.EMAIL: EmailActionHandler(),
            ActionType.WEBHOOK: WebhookActionHandler(),
            ActionType.GOOGLE_CHAT: GoogleChatActionHandler(),
        }

    def execute_action(self, db: Session, action: Action, log: Log) -> bool:
        """
        Execute a single action.

        Args:
            db: Database session
            action: Action to execute
            log: Log that triggered the action

        Returns:
            True if action executed successfully
        """
        if not action.enabled:
            logger.warning(f"Action {action.id} is disabled, skipping")
            return False

        handler = self.handlers.get(action.action_type)

        if not handler:
            logger.error(f"No handler found for action type: {action.action_type}")
            return False

        logger.info(
            f"Executing {action.action_type.value} action {action.id} for log {log.id}"
        )

        try:
            # Execute the action
            result = handler.execute(action.config, log)
            success = result.get("success", False)

            # Record in alert history
            alert = AlertHistory(
                rule_id=action.rule_id,
                log_id=log.id,
                action_id=action.id,
                action_result=result,
                success=success,
            )
            db.add(alert)
            db.commit()

            if success:
                logger.info(f"Action {action.id} executed successfully")
            else:
                logger.error(f"Action {action.id} failed: {result.get('error')}")

            return success

        except Exception as e:
            logger.error(f"Error executing action {action.id}: {e}", exc_info=True)

            # Record failure in alert history
            alert = AlertHistory(
                rule_id=action.rule_id,
                log_id=log.id,
                action_id=action.id,
                action_result={"error": str(e)},
                success=False,
            )
            db.add(alert)
            db.commit()

            return False


# Singleton instance
_action_handler: Optional[ActionHandlerService] = None


def get_action_handler() -> ActionHandlerService:
    """
    Get singleton action handler instance.

    Returns:
        ActionHandlerService instance
    """
    global _action_handler

    if _action_handler is None:
        _action_handler = ActionHandlerService()

    return _action_handler
