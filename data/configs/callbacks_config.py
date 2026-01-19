import os
from loguru import logger
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler
from langchain_core.callbacks.base import BaseCallbackHandler

load_dotenv(find_dotenv())

class LangFuseConfig(BaseSettings):
    USE_LANGFUSE: bool = True
    LANGFUSE_BASE_URL: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LangSmithConfig(BaseSettings):
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = None
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

class GlobalCallbacksService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.langfuse_config = LangFuseConfig()
        self.langsmith_config = LangSmithConfig()
        logger.info('LangFuseConfig и LangSmithConfig инциализированы')
        
        self.callbacks: list[BaseCallbackHandler] = []
        self.langfuse_handler: Optional[CallbackHandler] = None

        self._init_langsmith()
        self._init_langfuse()

        self._initialized = True

    def _init_langsmith(self) -> None:
        if not self.langsmith_config.LANGCHAIN_TRACING_V2:
            logger.info("LangSmith tracing DISABLED")
            return

        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = self.langsmith_config.LANGCHAIN_API_KEY or ""
        os.environ["LANGCHAIN_PROJECT"] = self.langsmith_config.LANGCHAIN_PROJECT or ""
        os.environ["LANGCHAIN_ENDPOINT"] = self.langsmith_config.LANGCHAIN_ENDPOINT

        logger.success(
            f"LangSmith ENABLED | project={self.langsmith_config.LANGCHAIN_PROJECT}"
        )

    def _init_langfuse(self) -> None:
        if not self.langfuse_config.USE_LANGFUSE:
            logger.info("Langfuse disabled")
            return

        try:
            Langfuse(
                public_key=self.langfuse_config.LANGFUSE_PUBLIC_KEY,
                secret_key=self.langfuse_config.LANGFUSE_SECRET_KEY,
                host=self.langfuse_config.LANGFUSE_BASE_URL,
            )
            self.client = get_client()
            self.langfuse_handler = CallbackHandler()
            self.callbacks.append(self.langfuse_handler)

            logger.success("Langfuse initialized")

        except Exception:
            logger.exception("Langfuse init failed")


