from loguru import logger
from langchain.tools import BaseTool
from langchain.messages import SystemMessage

from src.core.agents.models.base import (
    BaseLLM, 
    BaseTool, 
    Runnable,
    BaseAgent, 
    CreateAgent
)
from utils.decorators import retry_async
from src.models.messages import BaseMessage
from src.models.client_model import ClientModel
from data.configs.base_config import base_config
from src.core.agents.prompts import SummaryPromptTemplates
from data.configs.callbacks_config import CALLBACK_SERVICE

class SummaryAgent(BaseAgent):
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
        self.agent: Runnable | None = None
        self._ensure_agent()
        self._initialized = True
    
    def _ensure_agent(self) -> 'SummaryAgent':
        if self.agent is None:
            self.agent = CreateAgent.lc_create_agent(
                llm=self._llm,
                tools=self._tools
            ) 
        
    @retry_async(
        attempts=base_config.ATTEMPS_FOR_RETRY,
        backoff=base_config.BACKOFF,
        delay=base_config.DELAY
    )
    async def execute(
        self,
        user_message: BaseMessage,
        client_model: ClientModel,
    ):
        pass