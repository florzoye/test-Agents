import aiohttp
from src.enum.tg import TelegramParseMode
from data.configs.tg_config import TG_SETTINGS

TG_API_URL = f"https://api.telegram.org/bot{TG_SETTINGS.BOT_TOKEN}/sendMessage"

class TelegramSender:
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
                
