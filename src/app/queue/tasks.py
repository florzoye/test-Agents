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
    name="send_message_for_client",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def send_message_for_client(self, client_id: int, message: str) -> None:
    task_id = self.request.id
    redis_key = f"tg:task:{task_id}"

    status = redis_client.get(redis_key)
    if status == b"cancelled":
        return

    try:
        run_async(_send_tg_message_async(client_id, message))
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        redis_client.delete(redis_key)


@shared_task(name="cancel_scheduled_message")
def cancel_scheduled_message(task_id: str) -> bool:
    redis_key = f"tg:task:{task_id}"
    redis_client.set(redis_key, "cancelled", ex=3600)
    celery_app.control.revoke(task_id, terminate=False)
    return True