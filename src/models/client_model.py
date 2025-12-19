from typing import Optional, List

from src.models.messages import ClientMessage
from pydantic import BaseModel, Field, EmailStr, field_validator

class ClientModel(BaseModel):
    tg_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Telegram id"
    )

    instagram_nick: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=30,
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
        lt=120,
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
    message_history: List[ClientMessage] = Field(default_factory=list, description="История сообщений клиента")

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


    async def add_message(self, msg: ClientMessage):
        self.message_history.append(msg)



