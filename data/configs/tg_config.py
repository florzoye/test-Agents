import os
from loguru import logger
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    BOT_TOKEN: str
    session_name: str = "user_session"

    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )

    @property
    def send_message_url(self) -> str:
        return f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage"
    
TG_SETTINGS = TelegramSettings()
logger.info('TG_SETTINGS Инициализирован')