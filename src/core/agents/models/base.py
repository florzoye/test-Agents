from abc import ABC, abstractmethod

from langchain.agents import create_agent
from langchain.messages import SystemMessage
from langchain_classic.tools import BaseTool 
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel 

from src.models.messages import BaseMessage
from src.models.client_model import ClientModel

class BaseLLM(ABC):
    @abstractmethod
    def get_llm(self) -> BaseLanguageModel: ...

class BaseAgent(ABC):
    @abstractmethod
    def _ensure_agent(self) -> None: ...

    @abstractmethod
    async def execute(
        self,
        user_message: BaseMessage,
        client_model: ClientModel,
    ) -> BaseMessage:
        ...

class CreateAgent:
    @classmethod
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