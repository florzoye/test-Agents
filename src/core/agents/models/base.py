from abc import ABC, abstractmethod
from langchain_classic.tools import BaseTool 
from langchain_core.runnables import Runnable
from langchain_classic.base_language import BaseLanguageModel

class BaseLLM(ABC):
    @abstractmethod
    async def get_llm(self) -> BaseLanguageModel: ...

class BaseAgent(ABC):
    @abstractmethod
    async def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: list[BaseTool]
    ) -> Runnable: ...