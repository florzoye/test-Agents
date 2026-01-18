from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

from langchain.agents.middleware.types import AgentMiddleware
from langchain.agents.middleware.tool_retry import ToolRetryMiddleware
from langchain.agents.middleware.model_fallback import ModelFallbackMiddleware

from data.configs import BASE_CONFIG

class MiddlewareConfig(BaseSettings):
    MAIN_MODEL: str
    FALLBACK_MODELS: List[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

MIDDLEWARE_CONFIG = MiddlewareConfig()

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
        self._append_middleware()
        self._initialized = True
    
    def _append_middleware(self) -> None:
        self._middleware_lst.append(
            ModelFallbackMiddleware(
                first_model=MIDDLEWARE_CONFIG.MAIN_MODEL,
                *MIDDLEWARE_CONFIG.FALLBACK_MODELS      
            ))
        
        self._middleware_lst.append(
            ToolRetryMiddleware(
                backoff_factor=BASE_CONFIG.BACKOFF,
                max_retries=BASE_CONFIG.ATTEMPS_FOR_RETRY
            )
        )
        return self._middleware_lst
    
    @property
    def middlewares(self):
        return self._middleware_lst

MIDDLEWARE_SERVICE = MiddlewareService()