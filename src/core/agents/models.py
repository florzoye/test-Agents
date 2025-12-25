from typing import Optional, List
from abc import ABC, abstractmethod

from langchain.tools import BaseTool
from langchain_core.runnables import Runnable
from langchain_core.language_models.base import BaseLanguageModel


class BaseLLM(ABC):
    @abstractmethod
    async def get_llm(self) -> BaseLanguageModel:
        pass

class BaseAgent(ABC):
    @abstractmethod
    async def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: Optional[List[BaseTool]]
    ) -> Runnable:
        pass
