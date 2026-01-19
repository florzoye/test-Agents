import os
from loguru import logger
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from redis.asyncio import Redis
from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisSettings(BaseSettings):
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_HOST: str
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )

settings = RedisSettings()

redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

celery_app = Celery("celery_worker", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    enable_utc=True,
    timezone='Europe/Moscow',
    broker_connection_retry_on_startup=True,
)


redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASSWORD
)
import src.app.queue.tasks
logger.info('celery_app и redis_client инициализированы')