from abc import ABC, abstractmethod
from langchain.agents import create_agent
from langchain_classic.tools import BaseTool 
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel 

class BaseLLM(ABC):
    @abstractmethod
    def get_llm(self) -> BaseLanguageModel: ...

class BaseAgent(ABC):
    @abstractmethod
    def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: list[BaseTool]
    ) -> Runnable: ...

class CreateAgent(BaseAgent):
    def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: list[BaseTool]
    ) -> Runnable:
        llm_instance = llm.get_llm()
        agent = create_agent(
            model=llm_instance,
            tools=tools,
        )

        return agent