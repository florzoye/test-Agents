import asyncio
from typing import Any, Optional, Dict, TYPE_CHECKING
from abc import ABC, abstractmethod

from langchain_core.runnables import Runnable
from langchain.messages import SystemMessage, AnyMessage
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel 

from src.models.client_model import ClientModel
from src.models.messages import BaseMessage
from src.exceptions.agent_exp import AgentExecutionException

from src.factories.agent_factory import AgentFactory

from utils.decorators import retry_async
from utils.retry_handlers import log_retry_simple

class BaseLLM(ABC):
    _instance = None
    _response_format: Any = None 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @abstractmethod
    async def get_llm(self) -> BaseChatModel:
        ...

    def with_structured_output(
        self, 
        schema: type, 
        method: str = "json_schema", 
        include_raw: bool = False
    ) -> "BaseLLM":
        """
        Устанавливает Pydantic/TypedDict/JSON schema для structured output.
        """
        self._response_format = {
            "schema": schema,
            "method": method,
            "include_raw": include_raw
        }
        return self


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

        from data.init_configs import get_config
        base_config = get_config().BASE_CONFIG

        self._execution_semaphore = asyncio.Semaphore(
            base_config.MAX_CONCURRENT_EXECUTE
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
    ) -> BaseMessage | dict | BaseModel: ...

    async def execute(
        self, 
        client_model: ClientModel, 
        user_message: BaseMessage
    ) -> BaseMessage | Dict | BaseModel:
        
        from data.init_configs import get_config
        base_config = get_config().BASE_CONFIG
        runnable_config = get_config().RUNNABLE_CONFIG

        @retry_async(
            on_retry=log_retry_simple,
            attempts=base_config.ATTEMPS_FOR_RETRY,
            backoff=base_config.BACKOFF,
            delay=base_config.DELAY,
        )
        async def _execute_with_retry():
            await self._ensure_agent_async()

            async with self._execution_semaphore:
                try:
                    messages = await self._build_messages(client_model, user_message)
                    result_raw: dict = await self.agent.ainvoke(
                        {"messages": messages},
                        config=runnable_config,
                    )

                    return await self._get_model_response_result(
                        result_raw,
                        client_model=client_model,
                    )

                except AgentExecutionException:
                    raise
                except Exception as exp:
                    raise self._get_execute_exception(exp)

        return await _execute_with_retry()

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