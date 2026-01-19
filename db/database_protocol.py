from typing import List, Optional
from abc import ABC, abstractmethod

from src.models.client_model import ClientModel
from src.models.messages import BaseMessage


class ClientBase(ABC):

    @abstractmethod
    async def create_tables(self) -> bool:
        """Создать таблицы в базе данных"""
        ...

    @abstractmethod
    async def add_client(self, client: ClientModel) -> bool:
        """Добавить нового клиента"""
        ...

    @abstractmethod
    async def get_client(self, tg_id: int) -> Optional[ClientModel]:
        """Получить клиента по tg_id"""
        ...

    @abstractmethod
    async def get_all_client(self) -> List[ClientModel]:
        """Получить всех клиентов"""
        ...

    @abstractmethod
    async def client_exists(self, tg_id: int) -> bool:
        """Проверить существование клиента"""
        ...

    @abstractmethod
    async def update_client_fields(self, tg_id: int, **fields) -> bool:
        """Обновить произвольные поля клиента"""
        ...

    @abstractmethod
    async def update_lead_status(self, tg_id: int, new_status: str) -> bool:
        """Обновить статус лида"""
        ...

    @abstractmethod
    async def update_project_info(self, tg_id: int, project_info: str) -> bool:
        """Обновить информацию о проекте"""
        ...

    @abstractmethod
    async def get_message_history(self, tg_id: int) -> List[BaseMessage]:
        """Получить историю сообщений клиента"""
        ...

    @abstractmethod
    async def update_message_history(self, tg_id: int, history: List[BaseMessage]) -> bool:
        """Обновить всю историю сообщений"""
        ...

    @abstractmethod
    async def delete_client(self, tg_id: int) -> bool:
        """Удалить клиента"""
        ...

    @abstractmethod
    async def delete_all(self) -> bool:
        """Удалить всех клиентов"""
        ...

    @abstractmethod
    async def delete_all_tables(self) -> bool:
        """Удалить все таблицы"""
        ...
