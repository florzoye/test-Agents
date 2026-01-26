import logging
from fastmcp import FastMCP
from typing import Optional, List
from src.models.messages import BaseMessage
from src.models.client_model import ClientModel
from src.app.queue.scheduler import schedule_tg_message, cancel_message
from utils.database_repo import get_database_repo

log = logging.getLogger("mcp")
server = FastMCP('Tools For Agents')

ALLOWED_UPDATE_FIELDS = {
    "tg_nick",
    "email",
    "full_name",
    "age",
    "client_project_info",
    "lead_status"
}

### DATABASE tools (recource)
@server.tool
async def save_message_to_db(
    tg_id: int | str,
    source: str,
    message: str
) -> bool:
    """Сохраняет сообщение пользователя в историю.

    Args:
        tg_id: Telegram ID клиента
        source: Источник сообщения, должен быть 'client' или 'bot'
        message: Текст сообщения
        
    Returns:
        True если сообщение сохранено успешно, False в противном случае
    """
    if source not in {"client", "bot"}:
        return False

    db_repo = await get_database_repo()

    if not await db_repo.client_exists(tg_id):
        return False

    return await db_repo.update_message_history(tg_id, source, message)

@server.tool   
async def update_client_field(
    tg_id: int | str,
    *,
    tg_nick: Optional[str] = None,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    age: Optional[int] = None,
    client_project_info: Optional[str] = None,
    lead_status: Optional[str] = None
) -> bool:
    """Обновляет одно или несколько полей клиента.
    
    Args:
        tg_id: Telegram ID клиента
        tg_nick: Ник в Instagram (опционально)
        email: Email клиента (опционально)
        full_name: Полное имя клиента (опционально)
        age: Возраст клиента в годах (опционально)
        client_project_info: Информация о проекте клиента (опционально)
        lead_status: Статус лида - new, qualified или not_interested (опционально)
        
    Returns:
        True если обновление прошло успешно, False в противном случае
    """
    db_repo = await get_database_repo()

    valid_fields = {
        k: v
        for k, v in locals().items()
        if k in ALLOWED_UPDATE_FIELDS and v is not None
    }

    if not valid_fields:
        return False

    if not await db_repo.client_exists(tg_id):
        return False

    return await db_repo.update_client_fields(tg_id, **valid_fields)

@server.tool
async def update_client_lead(
    tg_id: int | str,
    lead_status: str
) -> bool:
    """Обновляет статус лида клиента.
    
    Args:
        db: Database или ClientBase объект для работы с БД
        tg_id: Telegram ID клиента
        lead_status: Новый статус лида - new, qualified или not_interested
        
    Returns:
        True если обновление прошло успешно, False в противном случае
    """
    db_repo = await get_database_repo()

    if not await db_repo.client_exists(tg_id):
        return False
    
    return await db_repo.update_lead_status(
        tg_id=tg_id, new_status=lead_status
    )

@server.tool
async def send_telegram_message(
    tg_id: int, 
    message: str, 
    delay_min: Optional[int] = None
) -> bool:
    """Отправляет сообщение клиенту в Telegram с задержкой или без.
    
    Args:
        tg_id: Telegram ID клиента
        message: Текст сообщения для клиента
        delay_min: Задержка отправки в секундах. Если None, отправляется сразу (опционально)
        
    Returns:
        True если сообщение запланировано успешно, False в противном случае
        
    Examples:
        -Отправить сразу: send_telegram_message(123, "Привет") \n
        -Отправить через 5 часов: send_telegram_message(123, "Готовы?", 18000)
    """
    if delay_min is None:
        delay_min = 1
        
    return bool(
        schedule_tg_message(
            tg_id=tg_id,
            message=message,
            delay_min=delay_min
        )
    )

@server.tool
async def cancel_last_scheduler_message(tg_id: int) -> bool:
    """Отменяет последнее запланированное сообщение для клиента.
    
    Args:
        tg_id: Telegram ID клиента
        
    Returns:
        True если сообщение отменено успешно, False в противном случае
    """
    return bool(
        cancel_message(
            tg_id=tg_id
        )
    )

@server.resource("clients/{tg_id}")
async def get_client(tg_id: int | str) -> ClientModel:
    db_repo = await get_database_repo()
    return await db_repo.get_client(tg_id)

@server.resource('clients/{tg_id}/messages')
async def get_client_messages(tg_id: int | str) -> List[BaseMessage]:
    db_repo = await get_database_repo()
    return await db_repo.get_message_history(tg_id)

async def start_mcp() -> None:
    log.info("FastMCP server starting...")
    server.run(transport="http", host="127.0.0.1", port=8000)