from src.app.queue.tasks import send_message_for_client, cancel_scheduled_message
from data.configs.redis_config import redis_client

def schedule_message(client_id: int, message: str, delay_seconds: int) -> str:
    result = send_message_for_client.apply_async(
        args=[client_id, message],
        countdown=delay_seconds
    )
    redis_client.setex(f"tg:task:{result.id}", delay_seconds + 300, "active")
    return result.id

def cancel_message(task_id: str) -> bool:
    cancel_scheduled_message.delay(task_id)
    return True