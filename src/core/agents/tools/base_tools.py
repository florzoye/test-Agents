from typing import Any
from langchain.tools import tool

from db.database import Database
from src.models.messages import BaseMessage
from db.database_protocol import ClientBase
from src.models.client_model import ClientModel

from src.app.queue.scheduler import schedule_message
from data.configs.redis_config import redis_client

@tool
async def get_user_model(db: Database | ClientBase, tg_id: int | str) -> ClientModel:
    """Получает модель клиента по его tg_id"""
    if await db.client_exists(tg_id) is False:
        return 'Пользователь не найден, возможно он новый. Проведи разведывочную беседу.'
    return await db.client_exists(tg_id)

@tool
async def get_messages(db: Database | ClientBase, tg_id: int | str) -> list[BaseMessage]:
    """Получает историю сообщений клиента по его tg_id"""
    if await db.client_exists(tg_id) is False:
        return []
    return await db.get_message_history(tg_id)

@tool
async def save_message(
    db: Database | ClientBase,
    tg_id: int | str,
    source: str,
    message: str
) -> bool:
    """
    Сохраняет сообщение пользователя по его tg_id

    :param tg_id: Идентификатор пользователя в Telegram
    :param source: Источник сообщения (строго, "user" или "bot")
    :param message: Текст сообщения
    """
    if await db.client_exists(tg_id) is False:
        return False
    return await db.update_message_history(tg_id, source, message)

@tool
async def update_user_field(
    db: Database | ClientBase,
    tg_id: int | str,
    **fields: Any
) -> bool:
    """
    Обновляет поле/поля пользователя по его tg_id, можно передовать несколько полей одним вызовом, 
    но только, те поля, которые есть в модели ClientModel (\n
        tg_id (Optional[int]): Telegram id 
        instagram_nick (Optional[str]): Ник в инстаграмме
        email (Optional[EmailStr]): Почта клиента
        full_name (Optional[str]): Полное имя клиента
        age (Optional[int]): Возраст клиента в годах
        client_project_info (Optional[str]): Минимальная информация о проекте клиента
        lead_status (str): Статус лида: new, qualified, not_interested
        message_history (List[BaseMessage]): История сообщений клиента
    )
    
    :param tg_id: Telegram ID пользователя
    :param fields: поля для обновления, например:
        full_name="Иван Иванов", email="ivan@example.com"
    :return: True если обновление прошло успешно, False если ошибка или пользователь не найден
    """
    valid_fields = {k: v for k, v in fields.items() if k in ClientModel.model_fields}
    if not valid_fields:
        return False  

    if not await db.client_exists(tg_id):
        return False  
    return await db.update_client_fields(tg_id, **valid_fields)

@tool
async def send_telegram_message():
    ...

base_tools = [
    save_message, 
    get_user_model, 
    get_messages, 
    update_user_field,
    send_telegram_message
]