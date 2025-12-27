import aiohttp
from enum import StrEnum
from data.configs.tg_config import tg_settings
from src.models.base.message_sender import MessageSender

class TelegramParseMode(StrEnum):
    HTML = "HTML"
    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    NONE = None  

class TelegramSender(MessageSender):
    async def send_message(
        self,
        content: str | None = None,
        recipient_id: str | None = None, 
        parse_mode: TelegramParseMode = TelegramParseMode.NONE,
    ) -> bool:
        tg_api_url = f"https://api.telegram.org/bot{tg_settings.BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": recipient_id,
            "text": content,
            'parse_mode': parse_mode
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                tg_api_url, 
                json=payload
            ) as response:
                if response.status == 200:
                    return True
                else:
                    return False
    async def check_delivery_status(self, message_id):
        ...
