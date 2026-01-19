from loguru import logger
from data.init_configs import CALLBACK_SERVICE
from langchain_core.runnables import RunnableConfig

RUNNABLE_CONFIG = RunnableConfig(
    callbacks=CALLBACK_SERVICE.callbacks,
)
logger.info('RUNNABLE_CONFIG Инициализирован')
