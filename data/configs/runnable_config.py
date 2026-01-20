from loguru import logger
from langchain_core.runnables import RunnableConfig

def build_runnable_config(callbacks):
    logger.info('RUNNABLE_CONFIG Инициализирован')
    return RunnableConfig(callbacks=callbacks)
