from typing import List
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class LLMAdapter(ABC):
    @abstractmethod
    async def apply(self, llm: BaseChatModel) -> BaseChatModel:
        ...

    def __or__(self, other: "LLMAdapter | LLMAdapterPipeline"):
        if isinstance(other, LLMAdapter):
            return LLMAdapterPipeline([self, other])
        elif isinstance(other, LLMAdapterPipeline):
            return LLMAdapterPipeline([self] + other.adapters)
        else:
            raise TypeError(f"Cannot pipe {type(other)}")

class LLMAdapterPipeline:
    def __init__(self, adapters: List[LLMAdapter]):
        self.adapters = adapters

    def __or__(self, other: "LLMAdapter | LLMAdapterPipeline"):
        if isinstance(other, LLMAdapter):
            return LLMAdapterPipeline(self.adapters + [other])
        elif isinstance(other, LLMAdapterPipeline):
            return LLMAdapterPipeline(self.adapters + other.adapters)
        else:
            raise TypeError(f"Cannot pipe {type(other)}")

    async def apply(self, llm: BaseChatModel) -> BaseChatModel:
        for adapter in self.adapters:
            llm = await adapter.apply(llm)
        return llm
