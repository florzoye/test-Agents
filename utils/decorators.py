import asyncio
import logging
import random
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar("T")
logger = logging.getLogger(__name__)

def retry_async(
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    *,
    max_delay: float | None = None,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except asyncio.CancelledError:
                    raise

                except retry_on as e:
                    if attempt >= attempts:
                        logger.error(
                            "Retry failed",
                            extra={
                                "function": func.__name__,
                                "attempts": attempts,
                            }
                        )
                        raise

                    logger.warning(
                        "Retry attempt",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "delay": current_delay,
                            "error": str(e),
                        }
                    )

                    if on_retry:
                        on_retry(attempt, e)

                    await asyncio.sleep(current_delay)

                    current_delay *= backoff
                    if max_delay:
                        current_delay = min(current_delay, max_delay)

                    current_delay *= random.uniform(0.8, 1.2)

        return wrapper
    return decorator
