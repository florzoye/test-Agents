import aiohttp
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

async def send_telegram_message(chat_id: int, text: str) -> dict:
    """
    Отправляет сообщение в Telegram через Bot API
    
    Args:
        chat_id: ID чата
        text: Текст сообщения
    Returns:
        Ответ от Telegram API
    """
    if not tg_settings.BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")
    
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
                async with session.post(tg_settings.send_message_url, json=payload) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        print(f"❌ Telegram API вернул ошибку: {response.status} - {response_text}")
                        raise HTTPException(status_code=response.status, detail="Ошибка Telegram API")
                    return await response.json()
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения в Telegram: {str(e)}")
        raise

@router.post("/tg_webhook")
async def telegram_webhook(update: TelegramUpdate):
    """
    Основной обработчик webhook от Telegram
    
    Принимает сообщение и отправляет эхо-ответ
    """
    try:
        
        message_data = None
        update_type = None
        
        if update.message:
            message_data = update.message
            update_type = "message"
        elif update.edited_message:
            message_data = update.edited_message
            update_type = "edited_message"
        elif update.channel_post:
            message_data = update.channel_post
            update_type = "channel_post"
        
        if not message_data:
            return {"status": "no_data"}
        
        chat_id = message_data.get("chat", {}).get("id")
        message_id = message_data.get("message_id")
        text = message_data.get("text", "")
        
        # Получаем информацию о пользователе
        from_user = message_data.get("from", {})
        user_id = from_user.get("id")
        username = from_user.get("username", "без username")
        first_name = from_user.get("first_name", "")
        last_name = from_user.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or f"User_{user_id}"
        
        # Получаем информацию о чате
        chat_info = message_data.get("chat", {})
        chat_type = chat_info.get("type", "unknown")
        chat_title = chat_info.get("title", "Личный чат")
        
        # Логируем информацию
        print(f"🔄 Тип обновления: {update_type}")
        print(f"👤 Пользователь: {full_name} (@{username})")
        print(f"🆔 User ID: {user_id}")
        print(f"💬 Chat ID: {chat_id} (тип: {chat_type}, название: {chat_title})")
        print(f"📝 Message ID: {message_id}")
        print(f"✉️ Текст сообщения: {text}")
        print("-" * 60)
        
        # Проверяем, есть ли текст для ответа
        if not text:
            print("⚠️ Сообщение без текста, отправляю приветствие")
            response_text = "👋 Привет! Я получил твое сообщение, но оно пустое. Напиши что-нибудь!"
        else:
            # Формируем эхо-ответ
            response_text = f"🔁 Эхо-ответ:\n\n{text}\n\n💡 PS: Это тестовый ответ от бота!"
        
        # Отправляем ответ пользователю
        print(f"📤 Отправляю ответ в чат {chat_id}...")
        send_result = await send_telegram_message(chat_id, response_text)
        
        print(f"✅ Ответ успешно отправлен!")
        print(f"📊 Результат: {send_result.get('ok', False)}")
        print("=" * 60)

        return {
            "status": "success",
            "chat_id": chat_id,
            "user": full_name,
            "message_received": text,
            "response_sent": True,
            "telegram_api_result": send_result
        }
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/tg_webhook")
async def verify_webhook():
    """
    GET endpoint для проверки работы webhook
    """
    return {
        "message": "Telegram webhook endpoint is active!",
        "instructions": "Use POST method with Telegram update JSON",
        "bot_token_configured": bool(tg_settings.BOT_TOKEN)
    }

@router.post("/send_message")
async def send_message(chat_id: int, text: str):
    """
    Ручная отправка тестового сообщения (для отладки)
    
    Пример запроса:
    POST /send_message
    {
        "chat_id": 123456789,
        "text": message_text
    }
    """
    try:
        result = await send_telegram_message(chat_id, text)
        return {
            "status": "success",
            "message": "Тестовое сообщение отправлено",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
