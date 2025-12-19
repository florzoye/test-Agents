import aiohttp
from typing import Optional

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from data.configs.tg_config import tg_settings

from db.session import SQLAlchemyManager
from db.crud import UsersORM
from src.models.client_model import ClientModel

manager = SQLAlchemyManager()
router = APIRouter()

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = Field(default=None)
    edited_message: Optional[dict] = Field(default=None)
    channel_post: Optional[dict] = Field(default=None)


@router.post("/tg_webhook")
async def telegram_webhook(update: TelegramUpdate):
    """
    POST endpoint для обработки входящих обновлений от Telegram
    """
    try:
        message = update.message or update.edited_message or update.channel_post
        if not message:
            return {"status": "ignored", "reason": "В сообщении нет данных"}
        
        manager.init()
        user_info = message.get("from", {})

        tg_id = user_info.get("id")
        username = user_info.get("username", "")
        message_date = message.get("date")
        context = message.get("text", "")

        async with manager.get_session() as session:
            users = UsersORM(session)
            if await users.user_exists(tg_id)

        return {
            "status": "success",
            "chat_id": chat_id,
            "user": 'full_name',
            "message_received": text,
            "response_sent": True,
            "telegram_api_result": 'send_result'
        }
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        raise HTTPException(status_code=500, detail="Произошла ошибка при обработке обновления Telegram")

@router.get("/tg_webhook")
async def verify_webhook():
    """
    GET endpoint для проверки работы webhook
    """
    return {
        "message": "Telegram webhook активен!",
        "instructions": "Отправьте POST запрос с обновлением Telegram для тестирования.",
        "bot_token_configured": bool(tg_settings.BOT_TOKEN)
    }

