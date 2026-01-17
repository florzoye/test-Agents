from loguru import logger
from langchain.tools import BaseTool
from langchain.messages import SystemMessage

from src.core.agents.models.base import (
    BaseLLM, 
    BaseTool, 
    Runnable,
    BaseAgent, 
)
from utils.decorators import retry_async
from src.models.messages import BaseMessage
from src.models.client_model import ClientModel
from src.core.agents.prompts import DialogPromptTemplates
from data.configs.callbacks_config import CALLBACK_SERVICE

class DialogAgent:
    def __init__(
        self,
        llm: BaseLLM,
        agent_factory: BaseAgent,
        tools: list[BaseTool],
    ):
        self._llm = llm
        self._tools = tools
        self._agent_factory = agent_factory
        self.agent: Runnable | None = None

    def init(self):
        self.agent = self._agent_factory.lc_create_agent(
            llm=self._llm,
            tools=self._tools,
        )
        
    @retry_async(attempts=3)
    async def execute(
        self,
        user_message: BaseMessage,
        client_model: ClientModel,
        system_prompt: SystemMessage
    ):
        if self.agent is None:
            raise RuntimeError("Agent not initialized, init() first!")

        try:
            messages = await DialogPromptTemplates.build_messages(
                client=client_model,
                message=user_message,
                system_prompt=system_prompt
            )

            result = await self.agent.ainvoke(
                {"messages": messages},
                config={"callbacks": CALLBACK_SERVICE.callbacks},
            )

            return result

        except Exception as e:
            logger.exception(e)
            return "Сервис временно недоступен"