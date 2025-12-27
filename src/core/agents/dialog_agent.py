from loguru import logger
from langchain.tools import BaseTool
from langchain.messages import SystemMessage

from src.core.agents.models.base import (
    BaseLLM, 
    BaseTool, 
    Runnable,
    BaseAgent, 
)
from src.models.messages import ClientMessage
from src.models.client_model import ClientModel
from src.core.agents.prompts import DialogPromptTemplates

from utils.decorators import retry_async

class DialogAgent:
    def __init__(
        self,
        llm: BaseLLM,
        agent_factory: BaseAgent,
        tools: list[BaseTool],
        langfuse_handler=None
    ):
        self._llm = llm
        self._agent_factory = agent_factory
        self._tools = tools
        self._langfuse_handler = langfuse_handler
        self.agent: Runnable | None = None

    async def init(self):
        self.agent = await self._agent_factory.lc_create_agent(
            llm=self._llm,
            tools=self._tools,
        )
    
    @retry_async(attempts=3)
    async def invoke(
        self,
        user_message: ClientMessage,
        client_model: ClientModel,
        system_prompt: SystemMessage
    ):
        if self.agent is None:
            raise RuntimeError("Agent not initialized")

        try:
            messages = await DialogPromptTemplates.build_messages(
                client=client_model,
                message=user_message,
                system_prompt=system_prompt
            )

            callbacks = [self._langfuse_handler] if self._langfuse_handler else []

            result = await self.agent.ainvoke(
                {"messages": messages},
                config={"callbacks": callbacks},
            )

            return result

        except Exception as e:
            logger.exception(e)
            return "Сервис временно недоступен"