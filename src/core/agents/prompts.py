import json
from langchain.messages import SystemMessage, HumanMessage, AIMessage

from src.models.messages import ClientMessage, Source
from src.models.client_model import ClientModel


class SystemPromptTemplate:
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
        message: ClientMessage,
        system_prompt: SystemMessage,
    ) -> list:

        messages: list = []

        messages.append(system_prompt)

        client_json = json.dumps(
            client.model_dump(exclude_none=True, exclude={"message_history"}),
            ensure_ascii=False,
            indent=2,
        )
        messages.append(
            SystemMessage(content=f"Данные клиента:\n{client_json}")
        )

        for msg in client.message_history or []:
            if not msg.content:
                continue

            if msg.source == Source.user:
                messages.append(HumanMessage(content=msg.content))
            elif msg.source == Source.agent:
                messages.append(AIMessage(content=msg.content))

        messages.append(
            HumanMessage(content=message.content)
        )

        return messages
