from typing import Annotated
from sqlalchemy import Integer, JSON, String
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.models.messages import BaseMessage

strnullable = Annotated[str | None, mapped_column(String, nullable=True)]

class Base(DeclarativeBase):
    def __repr__(self):
        col = [col for col in self.__table__.columns.keys()]
        return f'{self.__class__.__name__}(' + ', '.join(f'{c}={getattr(self, c)!r}' for c in col) + ')'


class Users(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_nick: Mapped[strnullable]
    email: Mapped[strnullable] 
    full_name: Mapped[strnullable] 
    client_project_info: Mapped[strnullable] 
    lead_status: Mapped[strnullable] 
    track_addresses: Mapped[list[BaseMessage]] = mapped_column(MutableList.as_mutable(JSON), default=[])