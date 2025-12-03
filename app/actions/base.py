"""Base action handler interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any

from app.models import Log


class BaseActionHandler(ABC):
    """Base class for action handlers."""

    @abstractmethod
    def execute(self, config: Dict[str, Any], log: Log) -> Dict[str, Any]:
        """
        Execute the action.

        Args:
            config: Action configuration dictionary
            log: Log that triggered the action

        Returns:
            Dictionary with execution result
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate action configuration.

        Args:
            config: Action configuration dictionary

        Returns:
            True if configuration is valid
        """
        pass
