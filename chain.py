from loguru import logger
from typing import TypedDict
from langgraph.graph import StateGraph

from src.models.messages import BaseMessage
from src.app.telegram_queue import telegram_event_queue

class State(TypedDict):
    pass


class MultiAgentChain:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return

    async def waiting_new_message(self, state: State):
        item: BaseMessage = await telegram_event_queue.get()
        logger.info('Очередь получила задачу, агент выполняет...')

    async def build_workflow(self):
        builder = StateGraph(State)

        builder.add_node('preprocessing_message', self.preprocessing_messages)
        builder.add_node('waiting_new_message', self.waiting_new_message)
        builder.add_node('continue_dialog', self.continue_dialog)

        return builder.compile()
    
    async def chec(self):
        graph  = await self.build_workflow()
        graph.ainvoke()
