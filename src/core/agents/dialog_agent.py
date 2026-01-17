from langchain.tools import BaseTool
from langchain.messages import SystemMessage

from data.configs.base_config import base_config
from data.configs.callbacks_config import CALLBACK_SERVICE

from utils.decorators import retry_async
from src.models.messages import BaseMessage
from src.models.client_model import ClientModel
from src.core.agents.models.exc import AgentEnum
from src.core.agents.prompts import DialogPromptTemplates
from src.core.agents.models.base import BaseLLM, BaseTool, Runnable, BaseAgent, CreateAgent 
from src.core.agents.models.exc import AgentExecutionException, AgentInitializationException, LLMException

class DialogAgent(BaseAgent):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self, 
        llm: BaseLLM, 
        tools: list[BaseTool],
        system_prompt: SystemMessage
    ):
        if self._initialized:
            return
        
        self._llm = llm
        self._tools = tools
        self.system_prompt = system_prompt
        self.agent: Runnable | None = None

        self._ensure_agent()
        self._initialized = True
    
    def _ensure_agent(self) -> None:
        try:
            if self.agent is None:
                self.agent = CreateAgent.lc_create_agent(
                    llm=self._llm,
                    tools=self._tools
                )
        except Exception as exp:
            raise AgentInitializationException(agent=AgentEnum.DIALOG, exp=exp)

    @retry_async(
        attempts=base_config.ATTEMPS_FOR_RETRY,
        backoff=base_config.BACKOFF,
        delay=base_config.DELAY
    )
    async def execute(
        self, 
        client_model: ClientModel, 
        user_message: BaseMessage, 
    ) -> BaseMessage:
        try:
            messages = await DialogPromptTemplates.build_messages(
                client=client_model,
                message=user_message,
                system_prompt=self.system_prompt
            )
            try:
                result = await self.agent.ainvoke(
                    {"messages": messages},
                    config={"callbacks": CALLBACK_SERVICE.callbacks},
                )
            except Exception as exp:
                raise AgentExecutionException(agent=AgentEnum.DIALOG, exp=exp)
            return result
        except Exception as exp:
            raise LLMException(agent=AgentEnum.DIALOG, exp=exp)
