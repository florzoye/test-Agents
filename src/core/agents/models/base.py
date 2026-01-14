from abc import ABC, abstractmethod
from langchain.agents import create_agent
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

class CreateAgent(BaseAgent):
    async def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: list[BaseTool]
    ) -> Runnable:
        llm_instance = await llm.get_llm()
        agent = create_agent(
            model=llm_instance,
            tools=tools,
        )

        return agent