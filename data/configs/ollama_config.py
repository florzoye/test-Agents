import os
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class OllamaConfig(BaseSettings):
    OLLAMA_MODEL: str
    
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )

OLLAMA_CONFIG = OllamaConfig()
logger.info('OLLAMA_CONFIG Инициализирован')