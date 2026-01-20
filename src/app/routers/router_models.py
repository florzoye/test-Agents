import aiohttp
from src.enum.tg import TelegramParseMode
from data.init_configs import get_config

config = get_config()
BOT_TOKEN = config.TG_SETTINGS.bot_token
TG_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

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
                
