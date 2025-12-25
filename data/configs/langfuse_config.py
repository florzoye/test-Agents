import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

load_dotenv(find_dotenv())

class LangFuseConfig(BaseSettings):
    LANGFUSE_BASE_URL: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str

    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
    )

langfuse_config = LangFuseConfig()
Langfuse(
    public_key=langfuse_config.LANGFUSE_PUBLIC_KEY,
    secret_key=langfuse_config.LANGFUSE_SECRET_KEY,
    host=langfuse_config.LANGFUSE_BASE_URL,
)

langfuse = get_client()
langfuse_handler = CallbackHandler()
