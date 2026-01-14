import logging
import asyncio
from functools import wraps
from typing import TypeVar, Callable, Any


T = TypeVar("T")

def retry_async(
    attempts: int = None,  
    delay: float = 1.0,
    backoff: float = 2.0,
    default_value: Any = None,
):
    """
    Async retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_attempts = attempts if attempts is not None else 3
            current_delay = delay

            for attempt in range(retry_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < retry_attempts - 1:  
                        logging.warning(
                            f"Attempt {attempt + 1}/{retry_attempts} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay:.1f} seconds..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logging.error(
                            f"All {retry_attempts} attempts failed for {func.__name__}: {str(e)}"
                        )
                        raise e

            return default_value

        return wrapper

    return decorator

def with_langfuse(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        result = await func(self, *args, **kwargs)
        
        if hasattr(self, 'langfuse_handler'):
            self.langfuse_handler.flush()
        
        return result
    return wrapper