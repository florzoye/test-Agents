from typing import Optional
from langchain.tools import tool

from db.database import Database
from db.database_protocol import ClientBase
from src.app.queue.scheduler import schedule_tg_message, cancel_message

ALLOWED_UPDATE_FIELDS = {
    "tg_nick",
    "email",
    "full_name",
    "age",
    "client_project_info",
    "lead_status"
}


@tool(parse_docstring=True)
async def save_message(
    db: Database | ClientBase,
    tg_id: int | str,
    source: str,
    message: str
) -> bool:
    """Сохраняет сообщение пользователя в историю.
    
    Args:
        db: Database или ClientBase объект для работы с БД
        tg_id: Telegram ID клиента
        source: Источник сообщения, должен быть 'client' или 'bot'
        message: Текст сообщения
        
    Returns:
        True если сообщение сохранено успешно, False в противном случае
    """
    if source not in {"client", "bot"}:
        return False

    if isinstance(db, Database):
        db = db.get()

    if not await db.client_exists(tg_id):
        return False

    return await db.update_message_history(tg_id, source, message)

@tool(parse_docstring=True)
async def update_client_field(
    db: Database | ClientBase,
    tg_id: int | str,
    tg_nick: Optional[str] = None,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    age: Optional[int] = None,
    client_project_info: Optional[str] = None,
    lead_status: Optional[str] = None
) -> bool:
    """Обновляет одно или несколько полей клиента.
    
    Args:
        db: Database или ClientBase объект для работы с БД
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
    if isinstance(db, Database):
        db = db.get()

    # Собираем только те поля, которые переданы
    fields = {}
    if tg_nick is not None:
        fields['tg_nick'] = tg_nick
    if email is not None:
        fields['email'] = email
    if full_name is not None:
        fields['full_name'] = full_name
    if age is not None:
        fields['age'] = age
    if client_project_info is not None:
        fields['client_project_info'] = client_project_info
    if lead_status is not None:
        fields['lead_status'] = lead_status

    # Фильтруем только разрешённые поля
    valid_fields = {
        k: v for k, v in fields.items()
        if k in ALLOWED_UPDATE_FIELDS
    }

    if not valid_fields:
        return False

    if not await db.client_exists(tg_id):
        return False

    return await db.update_client_fields(tg_id, **valid_fields)

@tool(parse_docstring=True)
async def update_client_lead(
    db: Database | ClientBase,
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
    if isinstance(db, Database):
        db = db.get()

    if not await db.client_exists(tg_id):
        return False
    
    return await db.update_lead_status(
        tg_id=tg_id, new_status=lead_status
    )

@tool(parse_docstring=True)
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

@tool(parse_docstring=True)
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

db_tools = [
    save_message, 
    update_client_field,
    update_client_lead
]

tg_tools = [
    send_telegram_message,
    cancel_last_scheduler_message
]

dialog_tools = [*tg_tools, *db_tools]