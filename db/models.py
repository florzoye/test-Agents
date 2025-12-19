import logging
from enum import StrEnum
from typing import Annotated, Union, Optional, TypedDict

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import ForeignKey, Integer, JSON, String, UniqueConstraint, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models.client_model import ClientModel

strnullable = Annotated[str | None, mapped_column(String, nullable=True)]

class IdentifierType(StrEnum):
    telegram = "telegram"
    email = "email"
    instagram = "instagram"

class MessageDict(TypedDict):
    source: str
    content: str
    timestamp: str

class Base(DeclarativeBase):
    def __repr__(self):
        col = [col for col in self.__table__.columns.keys()]
        return f'{self.__class__.__name__}(' + ', '.join(f'{c}={getattr(self, c)!r}' for c in col) + ')'

class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)
    full_name: Mapped[strnullable]                                          # настоящее имя клиента
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[strnullable]
    email: Mapped[strnullable]
    instagram_nick: Mapped[strnullable]
    
    client_project_info: Mapped[strnullable]
    message_history: Mapped[list[MessageDict]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list
    )
    lead_status: Mapped[str] = mapped_column(String, default="new")  # new, qualified, not_interested

    identifiers: Mapped[list["UserIdentifier"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class UserIdentifier(Base):
    __tablename__ = "user_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    type: Mapped[IdentifierType] = mapped_column(
        Enum(IdentifierType, native_enum=False),
        nullable=False
    )

    value: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped["Users"] = relationship(back_populates="identifiers")

    __table_args__ = (
        UniqueConstraint("type", "value", name="uq_identifier"),
    )
    
def to_client_model(user: Users | None) -> Optional[ClientModel]:
    """
    Конвертирует SQLAlchemy Users -> ClientModel
    """
    if user is None:
        return None

    try:
        data = {
            "tg_id": user.tg_id,
            "full_name": user.full_name,
            "age": user.age,
            "username": user.username,
            "email": user.email,
            "instagram_nick": user.instagram_nick,
            "client_project_info": user.client_project_info,
            "lead_status": user.lead_status,
            "message_history": user.message_history or [],
        }
        # восстановление полей (TODO)
        if user.identifiers:
            for ident in user.identifiers:
                if ident.type == IdentifierType.telegram and not data["tg_id"]:
                    data["tg_id"] = int(ident.value)
                elif ident.type == IdentifierType.email and not data["email"]:
                    data["email"] = ident.value
                elif ident.type == IdentifierType.instagram and not data["instagram_nick"]:
                    data["instagram_nick"] = ident.value

        return ClientModel(**data)

    except Exception as e:
        logging.error(
            "Ошибка при конвертации Users -> ClientModel",
            exc_info=e
        )
        return None
