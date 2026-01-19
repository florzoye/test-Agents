import asyncio
from typing import Optional
from abc import ABC, abstractmethod

from langchain_core.runnables import Runnable
from langchain.messages import AIMessage, AnyMessage
from langchain_core.language_models import BaseChatModel 

from src.models.client_model import ClientModel
from src.models.messages import BaseMessage, Source
from src.exceptions.agent_exp import AgentExecutionException

from src.enum.exc import RetryExceptionsEnum
from src.factories.agent_factory import AgentFactory

from utils.decorators import retry_async
from utils.retry_handlers import log_retry_simple
from data.init_configs import BASE_CONFIG, RUNNABLE_CONFIG

class BaseLLM(ABC):
    _llm = None
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._llm = None
            cls._instance._initialized = False
        return cls._instance
    
    @abstractmethod
    def get_llm(self) -> BaseChatModel: ...

class BaseAgentSingleton(ABC):
    _instance: Optional['BaseAgentSingleton'] = None
    _init_lock: asyncio.Lock = asyncio.Lock()
    _execution_semaphore: asyncio.Semaphore = asyncio.Semaphore(BASE_CONFIG.MAX_CONCURRENT_EXECUTE)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, llm: BaseLLM, system_prompt=None):
        if getattr(self, "_agent_initialized", False):
            return

        self._llm = llm
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
                self.agent = await AgentFactory().lc_create_agent(
                    self._llm,
                    self.system_prompt,
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
        retry_on=RetryExceptionsEnum.AGENT_EXCEPTIONS.value,
        attempts=BASE_CONFIG.ATTEMPS_FOR_RETRY,
        backoff=BASE_CONFIG.BACKOFF,
        delay=BASE_CONFIG.DELAY,
    )
    async def execute(self, client_model: ClientModel, user_message: BaseMessage) -> BaseMessage:
        await self._ensure_agent_async()

        async with self._execution_semaphore:
            try:
                messages = await self._build_messages(client_model, user_message)
                result_raw: dict = await self.agent.ainvoke(
                    {"messages": messages},
                    config=RUNNABLE_CONFIG,
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
    
    def __repr__(self) -> str:
        agent_status = "initialized" if self._agent_initialized else "not initialized"
        tools_count = len(self._tools) if self._tools else 0
        
        return (
            f"{self.__class__.__name__}("
            f"agent={agent_status}, "
            f"tools={tools_count}, "
            f"llm={self._llm.__class__.__name__}, "
            f"max_concurrent={self._execution_semaphore._value})"
        )