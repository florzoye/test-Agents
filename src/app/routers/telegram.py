import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from data.configs.tg_config import tg_settings

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

    Пример структуры update:
    {'message_id':, 'from': {'id': , 'is_bot': , 'first_name': '', 'username': '', 
    'language_code': '', 'is_premium': }, 'chat': 
    {'id': , 'first_name': '', 'username': '', 'type': ''}, 'date': , 'text': ''}
    """
    try:
        message = update.message or update.edited_message or update.channel_post
        if not message:
            return {"status": "ignored", "reason": "В сообщении нет данных"}
        user_info = message.get("from", {})

        tg_id = user_info.get("id")
        username = user_info.get("username", "")
        message_date = datetime.datetime.fromtimestamp(message.get("date", datetime.datetime.now().timestamp()))
        context = message.get("text", "")
       
        return {
            "status": "success",
            "tg_id": tg_id,
            "username": username,
            "message_date": message_date.isoformat(),
            "context": context
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

