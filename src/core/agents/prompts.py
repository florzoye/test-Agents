import json
from langchain.messages import SystemMessage, HumanMessage, AIMessage

from src.models.client_model import ClientModel
from src.models.messages import BaseMessage, Source

class DialogSystemPromptTemplate:
    @staticmethod
    def get_system_prompt() -> SystemMessage:
        return SystemMessage(
            content=(
                "Ты — вежливый и полезный ассистент.\n"
                "Отвечай клиенту на русском языке.\n"
                "Используй информацию о клиенте, если она предоставлена.\n"
                "Если информации недостаточно — задай уточняющий вопрос."
            )
        )

class DialogPromptTemplates:
    @classmethod
    async def build_messages(
        cls,
        client: ClientModel,
        message: BaseMessage,
    ) -> list:

        messages: list = []

        client_json = json.dumps(
            client.model_dump(exclude_none=True, exclude={"message_history"}),
            ensure_ascii=False,
            indent=2,
        )
        messages.append(
            SystemMessage(content=f"Данные клиента:\n{client_json}, история сообщений асисстента и клиента далее.")
        )

        for msg in client.message_history or []:
            if not msg.content:
                continue

            if msg.source == Source.CLIENT:
                messages.append(HumanMessage(content=msg.content))
            elif msg.source == Source.AGENT:
                messages.append(AIMessage(content=msg.content))

        messages.append(
            HumanMessage(content=message.content)
        )

        return messages


class ResearchPromptTemplates: # TODO
    @classmethod
    async def build_message(
        cls,
        client: ClientModel,
        message: BaseMessage,
    ):
        messages: list = []

        client_json = json.dumps(
            client.model_dump(exclude_none=True, exclude={"message_history"}),
            ensure_ascii=False,
            indent=2,
        )
        messages.append(
            SystemMessage(content=f"Данные клиента:\n{client_json}, история сообщений асисстента и клиента далее.")
        )

        for msg in client.message_history or []:
            if not msg.content:
                continue

            if msg.source == Source.CLIENT:
                messages.append(HumanMessage(content=msg.content))
            elif msg.source == Source.AGENT:
                messages.append(AIMessage(content=msg.content))

        messages.append(
            HumanMessage(content=message.content)
        )
        print(messages)
        return messages 