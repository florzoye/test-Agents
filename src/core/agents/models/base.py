import asyncio
from typing import List, Optional
from abc import ABC, abstractmethod

from langchain.agents import create_agent
from langchain_classic.tools import BaseTool
from langchain_core.runnables import Runnable
from langchain.messages import AIMessage, AnyMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel 

from src.models.client_model import ClientModel
from src.models.messages import BaseMessage, Source
from src.core.agents.models.exc import AgentExecutionException, RetryExceptions

from utils.decorators import retry_async
from utils.retry_handlers import log_retry_simple
from data.configs.base_config import base_config
from data.configs.callbacks_config import CALLBACK_SERVICE


class BaseLLM(ABC):
    @abstractmethod
    def get_llm(self) -> BaseLanguageModel: ...

class CreateAgent:
    async def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: list[BaseTool],
        system_prompt: SystemMessage
    ) -> Runnable:
        llm_instance = await llm.get_llm()
        agent = create_agent(
            model=llm_instance,
            tools=tools,
            system_prompt=system_prompt
        )

        return agent

class BaseAgentSingleton(ABC):
    _instance: Optional['BaseAgentSingleton'] = None
    _init_lock: asyncio.Lock = asyncio.Lock()
    _execution_semaphore: asyncio.Semaphore = asyncio.Semaphore(base_config.MAX_CONCURRENT_EXECUTE)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, llm: BaseLLM, tools: Optional[List[BaseTool]] = None, system_prompt=None):
        if getattr(self, "_agent_initialized", False):
            return

        self._llm = llm
        self._tools = tools or [] 
        self.system_prompt = system_prompt
        self.agent: Optional[Runnable] = None
        self._agent_initialized: bool = False

    async def _ensure_agent_async(self) -> None:
        if self._agent_initialized:
            return
        async with self._init_lock:
            if self._agent_initialized:
                return
            try:
                loop = asyncio.get_event_loop()
                self.agent = await loop.run_in_executor(
                    None,
                    CreateAgent.lc_create_agent,
                    self._llm,
                    self._tools,
                    self.system_prompt
                )
                self._agent_initialized = True
            except Exception as exp:
                raise self._get_init_exception(exp)

    @abstractmethod
    def _get_init_exception(self, exp: Exception) -> Exception:
        """кастомное исключение инициализации агента"""
        ...

    @abstractmethod
    async def _build_messages(self, client_model: ClientModel, user_message: BaseMessage) -> list[AnyMessage]:
        """список сообщений для LLM"""
        ...

    @retry_async(
        on_retry=log_retry_simple,
        retry_on=RetryExceptions.AGENT_EXCEPTIONS.value,
        attempts=base_config.ATTEMPS_FOR_RETRY,
        backoff=base_config.BACKOFF,
        delay=base_config.DELAY,
    )
    async def execute(self, client_model: ClientModel, user_message: BaseMessage) -> BaseMessage:
        await self._ensure_agent_async()

        async with self._execution_semaphore:
            try:
                messages = await self._build_messages(client_model, user_message)

                result_raw: dict = await self.agent.ainvoke(
                    {"messages": messages},
                    config={"callbacks": CALLBACK_SERVICE.callbacks},
                )

                ai_messages = [
                    msg for msg in result_raw.get("messages", [])
                    if isinstance(msg, AIMessage)
                ]

                content = ai_messages[-1].content if ai_messages else "Контент не получен"

                return BaseMessage(
                    content=content,
                    source=Source.agent,
                    tg_id=client_model.tg_id
                )

            except AgentExecutionException:
                raise
            except Exception as exp:
                raise self._get_execute_exception(exp)

    @abstractmethod
    def _get_execute_exception(self, exp: Exception) -> Exception:
        """кастомное исключение execute"""
        ...