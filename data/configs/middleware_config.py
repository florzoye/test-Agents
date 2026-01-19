import pkgutil
import importlib
from typing import List
from pathlib import Path
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

from langchain.agents.middleware.types import AgentMiddleware
from langchain.agents.middleware.tool_retry import ToolRetryMiddleware
from langchain.agents.middleware.model_fallback import ModelFallbackMiddleware

class MiddlewareConfig(BaseSettings):
    MAIN_MODEL: str
    FALLBACK_MODELS: List[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

MIDDLEWARE_CONFIG = MiddlewareConfig()
logger.info('MIDDLEWARE_CONFIG Инициализирован')

class MiddlewareService:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._middleware_lst: List[AgentMiddleware] = []
        self._initialized = True

    def _append_middleware(self) -> None:
        from src.core.agents.models.base import BaseLLM

        llms_path = Path(__file__).parent.parent / "llms"
        for _, module_name, _ in pkgutil.iter_modules([str(llms_path)]):
            importlib.import_module(f"data.llms.{module_name}")

        llm_instances = [cls().get_llm() for cls in BaseLLM.__subclasses__()]
        if not llm_instances:
            raise RuntimeError("Нет зарегистрированных LLM!")
        
        self._middleware_lst.append(ModelFallbackMiddleware(
            *llm_instances[::-1]
        ))

        from data.init_configs import BASE_CONFIG
        self._middleware_lst.append(
            ToolRetryMiddleware(
                backoff_factor=BASE_CONFIG.BACKOFF,
                max_retries=BASE_CONFIG.ATTEMPS_FOR_RETRY
            )
        )
        return self._middleware_lst

    @property
    def middlewares(self):
        if not self._middleware_lst:
            self._append_middleware()
        return self._middleware_lst
