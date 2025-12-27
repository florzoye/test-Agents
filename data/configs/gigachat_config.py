import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class GigaChatConfig(BaseSettings):
    GIGACHAT_AUTH_KEY: str
    GIGA_MODEL: str
    
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS" 

giga_chat_config = GigaChatConfig()