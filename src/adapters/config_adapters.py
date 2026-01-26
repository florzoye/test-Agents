from src.adapters.base import LLMAdapter
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig

class RunnableConfigAdapter(LLMAdapter):
    def __init__(
        self, 
        config: RunnableConfig,
    ):
      self._config = config

    async def apply(self, llm: BaseChatModel) -> BaseChatModel:
        return llm.with_config(
           config=self._config
        )