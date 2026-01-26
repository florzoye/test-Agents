from langchain.messages import AnyMessage, AIMessage, SystemMessage
from pydantic import BaseModel

from src.enum.client import Source
from src.models.messages import BaseMessage
from src.models.client_model import ClientModel
from src.core.agents.models.base import BaseAgentSingleton, BaseLLM
from src.core.agents.prompts import DialogPromptTemplates, ResearchPromptTemplates
from src.exceptions.agent_exp import AgentEnum, AgentInitializationException, LLMException

class DialogAgent(BaseAgentSingleton):
    def __init__(self, *, llm: BaseLLM, system_prompt: SystemMessage):
        super().__init__(llm=llm, system_prompt=system_prompt)

    def _get_init_exception(self, exp: Exception) -> Exception:
        return AgentInitializationException(agent=AgentEnum.DIALOG, exp=exp)

    def _get_execute_exception(self, exp: Exception) -> Exception:
        return LLMException(agent=AgentEnum.DIALOG, exp=exp, message="Ошибка при выполнении execute")

    async def _build_messages(self, client_model, user_message) -> list[AnyMessage]:
        return await DialogPromptTemplates.build_messages(
            client=client_model,
            message=user_message,
        )
    async def _get_model_response_result(self,result_raw: dict, *, client_model: ClientModel) -> dict:
        ai_messages = [
                msg for msg in result_raw.get("messages", [])
                if isinstance(msg, AIMessage)
            ]

        if not ai_messages:
            raise LLMException(
                agent=AgentEnum.DIALOG,
                message="LLM не вернула AIMessage"
            )

        return BaseMessage(
            content=ai_messages[-1].content,
            source=Source.agent,
            tg_id=client_model.tg_id,
        )

class ResearchAgent(BaseAgentSingleton):
    def __init__(self, *, llm: BaseLLM, system_prompt: SystemMessage):
        super().__init__(llm=llm, system_prompt=system_prompt)

    def _get_init_exception(self, exp: Exception) -> Exception:
        return AgentInitializationException(agent=AgentEnum.RESEARCH, exp=exp)

    def _get_execute_exception(self, exp: Exception) -> Exception:
        return LLMException(agent=AgentEnum.RESEARCH, exp=exp, message="Ошибка при выполнении execute")

    async def _build_messages(self, client_model, user_message) -> list[AnyMessage]:
        return await ResearchPromptTemplates.build_message(
            client=client_model,
            message=user_message,
        )
    
    async def _get_model_response_result(self, result_raw: dict, *, client_model: ClientModel) -> BaseModel:
        structured_response = result_raw.get("structured_response")
        if structured_response is None:
            raise LLMException(
                agent=AgentEnum.RESEARCH,
                message="LLM не вернула structured_response"
            )

        if isinstance(structured_response, BaseModel):
            return structured_response

        schema = getattr(self._llm, "_response_format", {}).get("schema")
        if schema is None:
            raise LLMException(
                agent=AgentEnum.RESEARCH,
                message="LLM не имеет _response_format для Pydantic модели"
            )

        return schema(**structured_response)

