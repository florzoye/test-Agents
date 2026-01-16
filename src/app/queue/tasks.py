import asyncio
from celery import shared_task

from data.configs.redis_config import redis_client, celery_app
from src.app.queue.utils import _send_tg_message_async


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.run_until_complete(coro)
    else:
        asyncio.run(coro)


@shared_task(
    name="send_tg_message_for_client",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def send_tg_message_for_client(self, tg_id: int, message: str) -> None:
    task_id = self.request.id
    redis_key = f"tg:task:{task_id}"

    if redis_client.get(redis_key) == b"cancelled":
        return

    try:
        run_async(_send_tg_message_async(tg_id, message))
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        redis_client.delete(redis_key)
        redis_client.delete(f"tg:scheduled:{tg_id}")


@shared_task(name="cancel_scheduled_message")
def cancel_scheduled_message(task_id: str) -> bool:
    task_key = f"tg:task:{task_id}"

    if not redis_client.exists(task_key):
        return False

    redis_client.set(task_key, "cancelled", ex=3600)
    celery_app.control.revoke(task_id, terminate=False)
    return True