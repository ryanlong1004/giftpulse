"""Celery tasks for monitoring Twilio logs."""

from app.tasks.celery_app import celery_app
from app.services.log_fetcher import get_log_fetcher
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.monitor.poll_twilio_logs")
def poll_twilio_logs():
    """
    Periodic task to poll Twilio API for new logs.

    This task runs at intervals defined in celery beat schedule.
    """
    logger.info("Starting Twilio log polling task")

    try:
        log_fetcher = get_log_fetcher()
        result = log_fetcher.fetch_and_store_recent_logs()

        logger.info(
            f"Polling complete: {result['total']} new logs saved "
            f"({result['calls']} calls, {result['messages']} messages, "
            f"{result['alerts']} alerts)"
        )

        return result

    except Exception as e:
        logger.error(f"Error in polling task: {e}", exc_info=True)
        raise


@celery_app.task(name="app.tasks.monitor.process_unprocessed_logs")
def process_unprocessed_logs():
    """
    Process logs that haven't been checked against monitoring rules.

    This task can be called manually or scheduled separately.
    """
    logger.info("Processing unprocessed logs")

    try:
        # Import here to avoid circular dependencies
        from app.services.pattern_matcher import get_pattern_matcher

        matcher = get_pattern_matcher()
        processed_count = matcher.process_unprocessed_logs()

        logger.info(f"Processed {processed_count} logs")

        return {"processed": processed_count}

    except Exception as e:
        logger.error(f"Error processing logs: {e}", exc_info=True)
        raise
