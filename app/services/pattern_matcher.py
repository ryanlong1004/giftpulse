"""Pattern matching engine for log analysis."""

import re
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db_context
from app.models import Log, MonitoringRule, PatternType, AlertHistory, Action
from app.utils.logger import get_logger
from app.utils.helpers import parse_error_codes, is_within_time_window

logger = get_logger(__name__)


class PatternMatcher:
    """Pattern matching engine for detecting log patterns."""

    def _match_error_code(self, log: Log, rule: MonitoringRule) -> bool:
        """
        Match log against error code pattern.

        Args:
            log: Log to check
            rule: Monitoring rule with error codes

        Returns:
            True if log matches pattern
        """
        if not log.error_code:
            return False

        error_codes = parse_error_codes(rule.pattern_value)
        return log.error_code in error_codes

    def _match_regex(self, log: Log, rule: MonitoringRule) -> bool:
        """
        Match log against regex pattern.

        Args:
            log: Log to check
            rule: Monitoring rule with regex pattern

        Returns:
            True if log matches pattern
        """
        try:
            pattern = re.compile(rule.pattern_value, re.IGNORECASE)

            # Check error message
            if log.error_message and pattern.search(log.error_message):
                return True

            # Check raw data (converted to string)
            raw_str = str(log.raw_data)
            if pattern.search(raw_str):
                return True

            return False

        except re.error as e:
            logger.error(f"Invalid regex pattern in rule {rule.id}: {e}")
            return False

    def _match_status(self, log: Log, rule: MonitoringRule) -> bool:
        """
        Match log against status pattern.

        Args:
            log: Log to check
            rule: Monitoring rule with status values

        Returns:
            True if log matches pattern
        """
        if not log.status:
            return False

        statuses = [s.strip().lower() for s in rule.pattern_value.split(",")]
        return log.status.lower() in statuses

    def _match_threshold(self, db: Session, log: Log, rule: MonitoringRule) -> bool:
        """
        Match log against threshold pattern.

        Args:
            db: Database session
            log: Log to check
            rule: Monitoring rule with threshold settings

        Returns:
            True if threshold is exceeded
        """
        if not rule.threshold_count or not rule.threshold_window_minutes:
            logger.warning(f"Threshold rule {rule.id} missing count or window")
            return False

        # Calculate time window
        window_start = log.timestamp - timedelta(minutes=rule.threshold_window_minutes)

        # Count matching logs in time window
        query = db.query(Log).filter(
            and_(
                Log.log_type == rule.log_type,
                Log.timestamp >= window_start,
                Log.timestamp <= log.timestamp,
            )
        )

        # Apply additional filters based on pattern_value if provided
        if rule.pattern_value:
            if rule.pattern_value.startswith("error_code:"):
                error_codes = parse_error_codes(
                    rule.pattern_value.replace("error_code:", "")
                )
                query = query.filter(Log.error_code.in_(error_codes))
            elif rule.pattern_value.startswith("status:"):
                statuses = rule.pattern_value.replace("status:", "").split(",")
                statuses = [s.strip() for s in statuses]
                query = query.filter(Log.status.in_(statuses))

        count = query.count()

        logger.debug(
            f"Threshold check: {count} logs in {rule.threshold_window_minutes}min "
            f"window (threshold: {rule.threshold_count})"
        )

        return count >= rule.threshold_count

    def check_log_against_rule(
        self, db: Session, log: Log, rule: MonitoringRule
    ) -> bool:
        """
        Check if a log matches a monitoring rule.

        Args:
            db: Database session
            log: Log to check
            rule: Monitoring rule to check against

        Returns:
            True if log matches rule
        """
        # Check if rule is enabled
        if not rule.enabled:
            return False

        # Check log type matches (if specified in rule)
        if rule.log_type and rule.log_type != log.log_type.value:
            return False

        # Match based on pattern type
        if rule.pattern_type == PatternType.ERROR_CODE:
            return self._match_error_code(log, rule)
        elif rule.pattern_type == PatternType.REGEX:
            return self._match_regex(log, rule)
        elif rule.pattern_type == PatternType.STATUS:
            return self._match_status(log, rule)
        elif rule.pattern_type == PatternType.THRESHOLD:
            return self._match_threshold(db, log, rule)

        return False

    def process_log(self, db: Session, log: Log) -> List[Action]:
        """
        Process a single log against all monitoring rules.

        Args:
            db: Database session
            log: Log to process

        Returns:
            List of actions to execute
        """
        actions_to_execute = []

        # Get all enabled rules
        rules = db.query(MonitoringRule).filter(MonitoringRule.enabled == True).all()

        logger.debug(f"Processing log {log.id} against {len(rules)} rules")

        for rule in rules:
            if self.check_log_against_rule(db, log, rule):
                logger.info(f"Log {log.id} matched rule {rule.name}")

                # Get enabled actions for this rule
                rule_actions = [action for action in rule.actions if action.enabled]

                actions_to_execute.extend(rule_actions)

        # Mark log as processed
        log.processed = True
        db.commit()

        return actions_to_execute

    def process_unprocessed_logs(self) -> int:
        """
        Process all unprocessed logs.

        Returns:
            Number of logs processed
        """
        with get_db_context() as db:
            # Get unprocessed logs
            logs = (
                db.query(Log)
                .filter(Log.processed == False)
                .order_by(Log.timestamp)
                .all()
            )

            logger.info(f"Processing {len(logs)} unprocessed logs")

            for log in logs:
                try:
                    actions = self.process_log(db, log)

                    # Execute actions
                    if actions:
                        from app.services.action_handler import get_action_handler

                        handler = get_action_handler()

                        for action in actions:
                            handler.execute_action(db, action, log)

                except Exception as e:
                    logger.error(f"Error processing log {log.id}: {e}", exc_info=True)
                    continue

            return len(logs)


# Singleton instance
_pattern_matcher: Optional[PatternMatcher] = None


def get_pattern_matcher() -> PatternMatcher:
    """
    Get singleton pattern matcher instance.

    Returns:
        PatternMatcher instance
    """
    global _pattern_matcher

    if _pattern_matcher is None:
        _pattern_matcher = PatternMatcher()

    return _pattern_matcher
