import os
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

load_dotenv(find_dotenv())

class LangFuseConfig(BaseSettings):
    LANGFUSE_BASE_URL: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str

    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )


class LangfuseService:
    def __init__(self):
        self.client = None
        self.handler = None

    def init(self, config):
        if self.client:
            return

        try:
            Langfuse(
                public_key=config.LANGFUSE_PUBLIC_KEY,
                secret_key=config.LANGFUSE_SECRET_KEY,
                host=config.LANGFUSE_BASE_URL,
            )

            self.client = get_client()
            self.handler = CallbackHandler()
            logger.info("Langfuse initialized")

        except Exception:
            logger.exception("Langfuse disabled")
            self.client = None
            self.handler = None