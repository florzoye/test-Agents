from src.app.queue.tasks import send_tg_message_for_client, cancel_scheduled_message
from data.configs.redis_config import redis_client

def schedule_tg_message(
    tg_id: int,
    message: str,
    delay_min: int | None = 1
) -> bool:
    try:
        user_key = f"tg:scheduled:{tg_id}"
        old_task_id = redis_client.get(user_key)
        _delay = delay_min or 0

        if old_task_id:
            cancel_scheduled_message.delay(old_task_id.decode())
            redis_client.delete(user_key)

        result = send_tg_message_for_client.apply_async(
            args=[tg_id, message],
            countdown=_delay
        )

        redis_client.setex(
            user_key,
            _delay + 60,
            result.id
        )

        redis_client.setex(
            f"tg:task:{result.id}",
            _delay + 60,
            "active"
        )

        return True

    except Exception:
        return False


def cancel_message(tg_id: int) -> bool:
    user_key = f"tg:scheduled:{tg_id}"
    task_id = redis_client.get(user_key)

    if not task_id:
        return False

    cancel_scheduled_message.delay(task_id.decode())
    redis_client.delete(user_key)
    return True