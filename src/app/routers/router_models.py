import aiohttp
from enum import Enum
from data.configs.tg_config import tg_settings
from src.models.base.message_sender import MessageSender

TG_API_URL = f"https://api.telegram.org/bot{tg_settings.BOT_TOKEN}/sendMessage"

class TelegramParseMode(Enum):
    HTML = "HTML"
    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    NONE = None  

class TelegramSender(MessageSender):
    async def send_message(
        self,
        content: str | None = None,
        chat_id: str | None = None, 
        parse_mode: TelegramParseMode | None = TelegramParseMode.MARKDOWN,
    ) -> bool:
        payload = {
            "chat_id": chat_id,
            "text": content,
            'parse_mode': parse_mode
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TG_API_URL, 
                json=payload
            ) as response:
                if response.status == 200:
                    return True
                else:
                    return False
                
    async def check_delivery_status(self, message_id): ...
