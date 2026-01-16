from typing import Optional, List, Union
from src.models.messages import BaseMessage
from pydantic import BaseModel, Field, EmailStr, field_validator

class ClientModel(BaseModel):
    """
    Модель клиента

    Args:
        tg_id (Optional[int]): Telegram id
        instagram_nick (Optional[str]): Ник в инстаграмме
        email (Optional[EmailStr]): Почта клиента
        full_name (Optional[str]): Полное имя клиента
        age (Optional[int]): Возраст клиента в годах
        client_project_info (Optional[str]): Минимальная информация о проекте клиента
        lead_status (str): Статус лида: new, qualified, not_interested
        message_history (List[BaseMessage]): История сообщений клиента
    """
    tg_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Telegram id"
    )

    instagram_nick: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Ник в инстаграмме"
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Почта клиента"
    )

    full_name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Полное имя клиента"
    )

    age: Optional[int] = Field(
        default=None,
        gt=0,
        lt=100,
        description="Возраст клиента в годах"
    )

    client_project_info: Optional[str] = Field(         # получать через суммирование 
        default=None,
        min_length=5,
        max_length=300,
        description='Минимальная информация о проекте клиента'
    )

    # Business
    lead_status: str = Field(default="new", description="Статус лида: new, qualified, not_interested")
    message_history: Union[List[BaseMessage], None] = Field(default_factory=list, description="История сообщений клиента")

    @field_validator("tg_id", mode="before")
    @classmethod
    def parse_tg_id(cls, v):
        if v is None:
            return v
        return int(v)

    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, v):
        if v is None:
            return v
        return " ".join(v.strip().split())


    async def add_message(self, msg: BaseMessage):
        self.message_history.append(msg)


def to_client_model(user: Union[dict, object, None]) -> Optional[ClientModel]:
    """
    Конвертирует dict или SQLAlchemy объект в ClientModel
    
    Args:
        user: dict из SQLite или SQLAlchemy ORM объект или None
        
    Returns:
        ClientModel или None
    """
    if not user:
        return None

    try:
        if isinstance(user, dict):
            data = user.copy()
        else:
            data = {k: v for k, v in user.__dict__.items() if not k.startswith("_")}

        if data.get("track_addresses") is None:
            data["track_addresses"] = []

        return ClientModel(**data)
        
    except Exception:
        return None