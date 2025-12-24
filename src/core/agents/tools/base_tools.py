from typing import Any
from langchain.tools import tool

from db.crud import UsersORM
from db.session import sqlalchemy_manager
from src.models.client_model import ClientModel
from src.models.messages import ClientMessage

from src.app.queue.scheduler import schedule_message
from data.configs.redis_config import redis_client

@tool
async def get_user_model(tg_id: int | str) -> ClientModel:
    """Получает модель клиента по его tg_id"""
    async with sqlalchemy_manager.get_session() as session:
        users_orm = UsersORM(session)
        if await users_orm.user_exists(tg_id) is False:
            return 'Пользователь не найден, возможно он новый. Проведи разведывочную беседу.'
        return await users_orm.get_user(tg_id)

@tool
async def get_messages(tg_id: int | str) -> list[ClientMessage]:
    """Получает историю сообщений клиента по его tg_id"""
    async with sqlalchemy_manager.get_session() as session:
        users_orm = UsersORM(session)
        if await users_orm.user_exists(tg_id) is False:
            return []
        return await users_orm.get_message_history(tg_id)

@tool
async def save_message(
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
    async with sqlalchemy_manager.get_session() as session:
        users_orm = UsersORM(session)
        if await users_orm.user_exists(tg_id) is False:
            return False
        return await users_orm.add_message_to_history(tg_id, source, message)

@tool
async def update_user_field(
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
        message_history (List[ClientMessage]): История сообщений клиента
    )
    
    :param tg_id: Telegram ID пользователя
    :param fields: поля для обновления, например:
        full_name="Иван Иванов", email="ivan@example.com"
    :return: True если обновление прошло успешно, False если ошибка или пользователь не найден
    """
    valid_fields = {k: v for k, v in fields.items() if k in ClientModel.model_fields}
    if not valid_fields:
        return False  

    async with sqlalchemy_manager.get_session() as session:
        users_orm = UsersORM(session)
        if not await users_orm.user_exists(tg_id):
            return False  # пользователь не найден
        return await users_orm.update_user_fields(tg_id, **valid_fields)

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