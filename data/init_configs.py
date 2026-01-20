from loguru import logger
from threading import Lock
from typing import Optional

from src.exceptions.config_exp import ConfigNotInitializedError

class ConfigRegistry:
    _instance: Optional['ConfigRegistry'] = None
    _lock = Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # без зависимостей
        self._base_config = None
        self._db_config = None
        self._tg_settings = None
        self._base_llm_config = None
        self._ollama_config = None
        self._giga_chat_config = None
        
        # с зависимостями
        self._redis_client = None
        self._celery_app = None
        self._middleware_service = None
        self._callback_service = None
        self._runnable_config = None

    def _init_simple_configs(self):
        """Инициализация конфигов без зависимостей"""
        from data.configs.base_config import BaseConfig
        from data.configs.database_config import DBConfig
        from data.configs.tg_config import TelegramSettings
        from data.configs.llm_config import BaseLLMConfig
        from data.configs.ollama_config import OllamaConfig
        from data.configs.gigachat_config import GigaChatConfig

        self._base_config = BaseConfig()
        logger.success('✓ BASE_CONFIG инициализирован')

        self._db_config = DBConfig()
        logger.success('✓ DB_CONFIG инициализирован')

        self._tg_settings = TelegramSettings()
        logger.success('✓ TG_SETTINGS инициализирован')

        self._base_llm_config = BaseLLMConfig()
        logger.success('✓ BASE_LLM_CONFIG инициализирован')

        self._ollama_config = OllamaConfig()
        logger.success('✓ OLLAMA_CONFIG инициализирован')

        self._giga_chat_config = GigaChatConfig()
        logger.success('✓ GIGA_CHAT_CONFIG инициализирован')

    def _init_redis(self):
        """Инициализация Redis и Celery"""
        from data.configs.redis_config import RedisSettings
        from redis.asyncio import Redis
        from celery import Celery

        settings = RedisSettings()
        redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

        self._celery_app = Celery("celery_worker", broker=redis_url, backend=redis_url)
        self._celery_app.conf.update(
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            enable_utc=True,
            timezone='Europe/Moscow',
            broker_connection_retry_on_startup=True,
        )

        self._redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            password=settings.REDIS_PASSWORD
        )
        
        logger.success('✓ REDIS_CLIENT и CELERY_APP инициализированы')

    def _init_services(self):
        """Инициализация сервисов с зависимостями"""
        from data.configs.callbacks_config import GlobalCallbacksService
        from data.configs.middleware_config import MiddlewareService
        from langchain_core.runnables import RunnableConfig
        
        self._callback_service = GlobalCallbacksService()
        self._callback_service.initialize()
        
        if self._callback_service.langsmith_config.LANGCHAIN_TRACING_V2:
            logger.success(
                f'✓ LangSmith ENABLED | project={self._callback_service.langsmith_config.LANGCHAIN_PROJECT}'
            )
        else:
            logger.info('✓ LangSmith tracing DISABLED')
            
        if self._callback_service.langfuse_config.USE_LANGFUSE:
            if self._callback_service.langfuse_handler:
                logger.success('✓ Langfuse initialized')
            else:
                logger.warning('⚠ Langfuse init failed')
        else:
            logger.info('✓ Langfuse disabled')
        
        logger.success('✓ CALLBACK_SERVICE инициализирован')

        self._runnable_config = RunnableConfig(
            callbacks=self._callback_service.callbacks
        )
        logger.success('✓ RUNNABLE_CONFIG инициализирован')

        self._middleware_service = MiddlewareService()
        self._middleware_service._append_middleware(self._base_config)
        logger.success('✓ MIDDLEWARE_SERVICE инициализирован')

    def initialize(self):
        """Полная инициализация всех конфигов"""
        if self._initialized:
            logger.warning('⚠ Конфигурация уже инициализирована, пропуск повторной инициализации')
            return

        with self._lock:
            if self._initialized:
                return

            logger.info('Начало инициализации конфигурации...')
            
            # сначала простые, потом сложные
            self._init_simple_configs()
            self._init_redis()
            
            self._initialized = True
            self._init_services()
            logger.success('🎉 Все конфигурации успешно инициализированы')

    @property
    def BASE_CONFIG(self):
        self._check_initialized()
        return self._base_config

    @property
    def DB_CONFIG(self):
        self._check_initialized()
        return self._db_config

    @property
    def TG_SETTINGS(self):
        self._check_initialized()
        return self._tg_settings

    @property
    def BASE_LLM_CONFIG(self):
        self._check_initialized()
        return self._base_llm_config

    @property
    def OLLAMA_CONFIG(self):
        self._check_initialized()
        return self._ollama_config

    @property
    def GIGA_CHAT_CONFIG(self):
        self._check_initialized()
        return self._giga_chat_config

    @property
    def redis_client(self):
        self._check_initialized()
        return self._redis_client

    @property
    def celery_app(self):
        self._check_initialized()
        return self._celery_app

    @property
    def MIDDLEWARE_SERVICE(self):
        self._check_initialized()
        return self._middleware_service

    @property
    def CALLBACK_SERVICE(self):
        self._check_initialized()
        return self._callback_service

    @property
    def RUNNABLE_CONFIG(self):
        self._check_initialized()
        return self._runnable_config

    def _check_initialized(self):
        if not self._initialized:
            raise ConfigNotInitializedError()

    @property
    def is_initialized(self) -> bool:
        """Проверка статуса инициализации"""
        return self._initialized


_registry: Optional[ConfigRegistry] = None


def init():
    """Инициализация всех конфигураций. Вызывать один раз при старте приложения."""
    global _registry
    if _registry is None:
        _registry = ConfigRegistry()
    _registry.initialize()


def get_config() -> ConfigRegistry:
    """Получение экземпляра реестра конфигов."""
    global _registry
    if _registry is None:
        _registry = ConfigRegistry()
    
    if not _registry.is_initialized:
        raise ConfigNotInitializedError()
    
    return _registry


__all__ = ['init', 'get_config']