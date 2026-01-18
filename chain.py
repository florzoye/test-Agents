from loguru import logger
from typing import TypedDict, Literal
from IPython.display import Image, display
from langgraph.graph import StateGraph, END

from src.models.client_model import ClientModel, to_client_model
from src.models.messages import BaseMessage
from src.app.telegram_queue import telegram_event_queue
from src.core.agents.models.base import BaseAgentSingleton
from db.database import database, Database, ClientBase

class State(TypedDict):
    message: BaseMessage | None
    client_info: dict | None
    preprocessed_data: dict | None
    response: str | None
    should_continue: bool


class MultiAgentChain:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        *, 
        db: Database | ClientBase,
        dialog_llm: BaseAgentSingleton,
        research_llm: BaseAgentSingleton,
    ):
        if self._initialized:
            return
        
        self.db = db
        self.dialog_llm = dialog_llm  
        self.research_llm = research_llm  
        self._initialized = True
        logger.info("MultiAgentChain инициализирован")

    async def waiting_new_message(self, state: State) -> State:
        logger.info("Агент ожидает новое сообщение...")
        item: BaseMessage = await telegram_event_queue.get()
        logger.info(f'Получено сообщение от пользователя: {item.tg_id}')

        return {
            **state,
            "message": item,
            "should_continue": True
        }

    async def preprocessing_message(self, state: State) -> State:
        logger.info("Начало препроцессинга сообщения")

        message = state.get("message")
        if not message:
            logger.warning("Сообщение отсутствует")
            return {**state, "should_continue": False}

        try:
            repo = self.db.get() if isinstance(self.db, Database) else self.db
        except Exception as exp:
            logger.error(f"Ошибка доступа к базе данных: {exp}")
            return {**state, "should_continue": False}

        # Получаем модель клиента из базы
        client_model = None
        try:
            client_model = await repo.get_client(message.tg_id)
            if client_model is None:
                client_model = ClientModel(
                    tg_id=getattr(message, "tg_id", message.tg_id),
                    tg_nick=getattr(message, "tg_nick", None)
                )
                client_model.add_message(message)
                await repo.add_client(client_model)
            else:
                client_model.add_message(message)
                await repo.update_message_history(
                    tg_id=client_model.tg_id, 
                    history=client_model.message_history
                )  
        except Exception as exp:
            logger.error(f"Ошибка при получении данных клиента: {exp}")
            return {**state, "should_continue": False}

        preprocessed_data = {
            "client_data": client_model,
            "message_history": client_model.message_history or [],
            "current_message": getattr(message, "content", "")
        }

        logger.info(f"Препроцессинг завершен для пользователя {message.tg_id}")
        return {
            **state,
            "preprocessed_data": preprocessed_data,
            "should_continue": True
        }

    async def build_workflow(self) -> StateGraph:
        """Построение workflow графа"""
        logger.info("Построение workflow")
        
        builder = StateGraph(State)

        # Добавляем узлы
        builder.add_node('waiting_new_message', self.waiting_new_message)
        builder.add_node('preprocessing_message', self.preprocessing_message)
        builder.add_node('research_message', self.research_message)
        builder.add_node('continue_dialog', self.continue_dialog)

        # Устанавливаем точку входа
        builder.set_entry_point('waiting_new_message')

        # Добавляем edges (переходы между узлами)
        builder.add_edge('waiting_new_message', 'preprocessing_message')
        builder.add_edge('preprocessing_message', 'research_message')
        
        # Условный переход после research
        builder.add_conditional_edges(
            'research_message',
            self.should_continue_processing,
            {
                "continue_dialog": "continue_dialog",
                "waiting_new_message": "waiting_new_message"
            }
        )
        
        builder.add_conditional_edges(
            'continue_dialog',
            self.after_dialog,
            {
                "waiting_new_message": "waiting_new_message",
                END: END
            }
        )

        logger.info("Workflow построен успешно")
        return builder.compile()
    
    async def run(self):
        """Запуск бесконечного цикла обработки сообщений"""
        logger.info("Запуск MultiAgentChain")
        graph = await self.build_workflow()
        
        initial_state: State = {
            "message": None,
            "tg_id": None,
            "client_info": None,
            "preprocessed_data": None,
            "response": None,
            "should_continue": True
        }
        
        while True:
            try:
                result = await graph.ainvoke(initial_state)
                logger.info(f"Итерация завершена: {result}")
            except Exception as e:
                logger.error(f"Ошибка в workflow: {e}")
                continue
    
    async def show_workflow(self):
        graph = await self.build_workflow()
        try:
            display(Image(graph.get_graph().draw_mermaid_png()))
        except ImportError:
            logger.warning("Для визуализации установите graphviz и IPython")
            logger.info("Граф построен, но визуализация недоступна")


async def main():
    agent = MultiAgentChain()
    await agent.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())