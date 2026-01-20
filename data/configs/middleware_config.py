import pkgutil
import importlib
from typing import List
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.agents.models.base import BaseLLM
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


class MiddlewareService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._middleware_lst: List[AgentMiddleware] = []
        self._initialized = False  

    def _append_middleware(self, base_config) -> List[AgentMiddleware]:
        if self._middleware_lst:
            return self._middleware_lst

        logger.info('Загрузка LLM модулей...')
        
        # Динамическая загрузка всех LLM модулей
        llms_path = "src/core/agents/llms"
        loaded_modules = []
        for _, module_name, _ in pkgutil.iter_modules([str(llms_path)]):
            try:
                importlib.import_module(f"src.core.agents.llms.{module_name}")
                loaded_modules.append(module_name)
            except Exception as e:
                logger.warning(f'⚠ Не удалось загрузить модуль {module_name}: {e}')
        
        if loaded_modules:
            logger.info(f'Загружено LLM модулей: {", ".join(loaded_modules)}')

        # Получаем все подклассы BaseLLM
        llm_classes = BaseLLM.__subclasses__()
        if not llm_classes:
            raise RuntimeError("Нет зарегистрированных LLM классов")
            
        logger.info(f'Найдено LLM классов: {[cls.__name__ for cls in llm_classes]}')
        
        # Создание инстансов LLM и получение реальных LLM объектов
        llm_instances = []
        for llm_class in llm_classes:
            try:
                wrapper = llm_class()
                llm = wrapper.get_llm()
                llm_instances.append(llm)
                logger.success(f'  ✓ {llm_class.__name__}')
            except Exception as e:
                logger.error(f'  ✗ Ошибка инициализации {llm_class.__name__}: {e}')
        
        if not llm_instances:
            raise RuntimeError("Не удалось инициализировать ни один LLM!")
        
        logger.info(f'Инициализировано {len(llm_instances)} LLM')
        
        # Добавление middleware
        self._middleware_lst.append(
            ModelFallbackMiddleware(*llm_instances[::-1])
        )
        logger.success(f'✓ ModelFallbackMiddleware ({len(llm_instances)} моделей)')

        self._middleware_lst.append(
            ToolRetryMiddleware(
                backoff_factor=base_config.BACKOFF,
                max_retries=base_config.ATTEMPS_FOR_RETRY
            )
        )
        logger.success(f'✓ ToolRetryMiddleware (retries={base_config.ATTEMPS_FOR_RETRY})')
        
        self._initialized = True
        return self._middleware_lst

    @property
    def middlewares(self) -> List[AgentMiddleware]:
        """Получение списка middleware"""
        if not self._middleware_lst:
            raise RuntimeError(
                "Middleware не инициализированы. Вызовите init() из data.init_configs"
            )
        return self._middleware_lst