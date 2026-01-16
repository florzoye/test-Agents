from src.app.routers.router_models import TelegramSender

async def _send_tg_message_async(
    tg_id: int | str, 
    message: str
) -> bool:
    sender = TelegramSender()
    return await sender.send_message(
        recipient_id=str(tg_id),
        content=message
    )