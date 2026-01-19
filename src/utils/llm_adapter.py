from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class LLMAdapter(ABC):
    @abstractmethod
    async def build(self, llm: BaseChatModel) -> BaseChatModel:
        ... 