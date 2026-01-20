import asyncio
from typing import Optional, Dict, TYPE_CHECKING
from abc import ABC, abstractmethod

from langchain_core.runnables import Runnable
from langchain.messages import SystemMessage, AnyMessage
from langchain_core.language_models import BaseChatModel 

from src.models.client_model import ClientModel
from src.models.messages import BaseMessage
from src.exceptions.agent_exp import AgentExecutionException

from src.factories.agent_factory import AgentFactory

from utils.decorators import retry_async
from utils.retry_handlers import log_retry_simple
from data.configs.base_config import BASE_CONFIG

class BaseLLM(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @abstractmethod
    async def get_llm(self) -> BaseChatModel:
        ...


class BaseAgentSingleton(ABC):
    _instance: Optional['BaseAgentSingleton'] = None
    _init_lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *, llm: BaseLLM, system_prompt: SystemMessage):
        if getattr(self, "_agent_initialized", False):
            return

        self._execution_semaphore = asyncio.Semaphore(
            BASE_CONFIG.MAX_CONCURRENT_EXECUTE
        )
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
    
    @abstractmethod
    async def _get_model_response_result(
        self,
        result_raw: dict,
        *,
        client_model: ClientModel,
    ) -> object: ...

    @retry_async(
        on_retry=log_retry_simple,
        attempts=BASE_CONFIG.ATTEMPS_FOR_RETRY,
        backoff=BASE_CONFIG.BACKOFF,
        delay=BASE_CONFIG.DELAY,
    )
    async def execute(self, client_model: ClientModel, user_message: BaseMessage) -> BaseMessage | Dict:
        await self._ensure_agent_async()
        from data.init_configs import  RUNNABLE_CONFIG

        async with self._execution_semaphore:
            try:
                messages = await self._build_messages(client_model, user_message)
                result_raw: dict = await self.agent.ainvoke(
                    {"messages": messages},
                    config=RUNNABLE_CONFIG,
                )

                return await self._get_model_response_result(
                    result_raw,
                    client_model=client_model,
                )
                # ai_messages = [
                #     msg for msg in result_raw.get("messages", [])
                #     if isinstance(msg, AIMessage)
                # ]

                # content = ai_messages[-1].content if ai_messages else "Контент не получен"

                # return BaseMessage(
                #     content=content,
                #     source=Source.agent,
                #     tg_id=client_model.tg_id
                # )

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