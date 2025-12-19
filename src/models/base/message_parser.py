from abc import ABC, abstractmethod
from typing import Optional

from src.models.client_model import ClientMessage


class MessageParser(ABC):
    @abstractmethod
    def get_new_message(self) -> Optional[ClientMessage]:
        """Получить новое сообщение из источника"""
        ...

    @abstractmethod
    def check_connection(self) -> bool:
        """Проверить, в порядке ли соединение с внешним источником"""
        ...

    @abstractmethod
    def fetch_history(self, client_id: str) -> list[ClientMessage]:
        """Получить историю сообщений клиента"""
        ...