import logging

logger = logging.getLogger(__name__)

def log_retry_simple(attempt: int, exc: Exception):
    logger.warning(f"Retry attempt {attempt} failed: {exc}")

