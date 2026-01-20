import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class BaseConfig(BaseSettings):
    DELAY: float
    BACKOFF: float
    ATTEMPS_FOR_RETRY: int
    MAX_CONCURRENT_EXECUTE: int

    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )