import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import redis
from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict



class RedisSettings(BaseSettings):
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_HOST: str
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, 'app/uploads')
    STATIC_DIR: str = os.path.join(BASE_DIR, 'app/static')
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )

settings = RedisSettings()

redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

celery_app = Celery("celery_worker", broker=redis_url, backend=redis_url)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASSWORD
)
