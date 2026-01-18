from typing import Optional, List
from langchain.tools import BaseTool
from langchain.messages import AnyMessage

from src.core.agents.tools.base_tools import dialog_tools
from src.core.agents.models.base import BaseAgentSingleton, BaseLLM
from src.core.agents.prompts import DialogPromptTemplates, ResearchPromptTemplates
from src.core.agents.models.exc import AgentEnum, AgentInitializationException, LLMException

class DialogAgent(BaseAgentSingleton):
    def __init__(self, llm: BaseLLM, tools: Optional[List[BaseTool]] = None, system_prompt=None):
        super().__init__(llm, tools=tools or dialog_tools, system_prompt=system_prompt)

    def _get_init_exception(self, exp: Exception) -> Exception:
        return AgentInitializationException(agent=AgentEnum.DIALOG, exp=exp)

    def _get_execute_exception(self, exp: Exception) -> Exception:
        return LLMException(agent=AgentEnum.DIALOG, exp=exp, message="Ошибка при выполнении execute")

    async def _build_messages(self, client_model, user_message) -> list[AnyMessage]:
        return await DialogPromptTemplates.build_messages(
            client=client_model,
            message=user_message,
            system_prompt=self.system_prompt
        )

class ResearchAgent(BaseAgentSingleton):
    def __init__(self, llm: BaseLLM, tools: Optional[List[BaseTool]] = None, system_prompt=None):
        super().__init__(llm, tools=tools or [], system_prompt=system_prompt)

    def _get_init_exception(self, exp: Exception) -> Exception:
        return AgentInitializationException(agent=AgentEnum.RESEARCH, exp=exp)

    def _get_execute_exception(self, exp: Exception) -> Exception:
        return LLMException(agent=AgentEnum.RESEARCH, exp=exp, message="Ошибка при выполнении execute")

    async def _build_messages(self, client_model, user_message) -> list[AnyMessage]:
        return await ResearchPromptTemplates.build_message(
            client=client_model,
            message=user_message,
            system_prompt=self.system_prompt
        )