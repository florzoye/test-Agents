from src.app.routers.router_models import TelegramSender

async def _send_tg_message_async(
    client_id: int, 
    message: str
) -> bool:
    sender = TelegramSender()
    return await sender.send_message(
        recipient_id=str(client_id),
        content=message
    )