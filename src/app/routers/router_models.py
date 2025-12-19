import aiohttp
from data.configs.tg_config import tg_settings

from src.models.base.message_sender import MessageSender

class TelegramSender(MessageSender):
    async def send_message(
        self, 
        recipient_id: str | None = None, 
        content: str | None = None
    ) -> bool:
        tg_api_url = f"https://api.telegram.org/bot{tg_settings.bot_token}/sendMessage"
        payload = {
            "chat_id": recipient_id,
            "text": content,
            'parse_mode': 'HTML'
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

class InstagramSender(MessageSender):
    async def send_message(
        self, 
        recipient_id: str | None = None, 
        content: str | None = None
    ) -> bool:
       ...
    
class GmailSender(MessageSender):
    async def send_message(
        self, 
        recipient_id: str | None = None, 
        content: str | None = None
    ) -> bool:
       ...