from langchain.messages import AnyMessage
from src.core.agents.models.base import BaseAgentSingleton
from src.core.agents.prompts import DialogPromptTemplates, SummaryPromptTemplates
from src.core.agents.models.exc import AgentEnum, AgentInitializationException, LLMException

class DialogAgent(BaseAgentSingleton):
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

class SummaryAgent(BaseAgentSingleton):
    def _get_init_exception(self, exp: Exception) -> Exception:
        return AgentInitializationException(agent=AgentEnum.SUMMARY, exp=exp)

    def _get_execute_exception(self, exp: Exception) -> Exception:
        return LLMException(agent=AgentEnum.SUMMARY, exp=exp, message="Ошибка при выполнении execute")

    async def _build_messages(self, client_model, user_message) -> list[AnyMessage]:
        return await SummaryPromptTemplates.build_message(
            client=client_model,
            message=user_message,
            system_prompt=self.system_prompt
        )