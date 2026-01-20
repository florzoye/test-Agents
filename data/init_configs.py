from data.configs.base_config import BASE_CONFIG 
from data.configs.database_config import DB_CONFIG
from data.configs.tg_config import TG_SETTINGS
from data.configs.redis_config import redis_client, celery_app
from data.configs.llm_config import BASE_LLM_CONFIG
from data.configs.ollama_config import OLLAMA_CONFIG
from data.configs.gigachat_config import GIGA_CHAT_CONFIG
from data.configs.runnable_config import build_runnable_config

from data.configs.middleware_config import MiddlewareService
from data.configs.callbacks_config import GlobalCallbacksService

MIDDLEWARE_SERVICE = None
CALLBACK_SERVICE = None
RUNNABLE_CONFIG = None

def init():
    global MIDDLEWARE_SERVICE, CALLBACK_SERVICE, RUNNABLE_CONFIG
    if MIDDLEWARE_SERVICE is None:
        from data.configs.middleware_config import MiddlewareService
        MIDDLEWARE_SERVICE = MiddlewareService()
        _ = MIDDLEWARE_SERVICE.middlewares

    if CALLBACK_SERVICE is None:
        from data.configs.callbacks_config import GlobalCallbacksService
        CALLBACK_SERVICE = GlobalCallbacksService()

    if RUNNABLE_CONFIG is None:
        from langchain_core.runnables import RunnableConfig
        RUNNABLE_CONFIG = RunnableConfig(callbacks=CALLBACK_SERVICE.callbacks)