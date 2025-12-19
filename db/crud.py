import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Users, to_client_model
from src.models.client_model import ClientModel, ClientMessage


class UsersORM:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    async def add_user(self, user: ClientModel) -> bool:
        try:
            user_dict = user.model_dump()
            
            # message_history в JSON
            message_history = [
                {
                    "source": msg.source,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in user_dict.get('message_history', [])
            ]
            
            obj = Users(
                tg_id=user_dict.get('tg_id'),
                message_history=message_history,
                age=user_dict.get('age'),
                full_name=user_dict.get('full_name'),
                username=user_dict.get('username'),
                email=user_dict.get('email'),
                instagram_nick=user_dict.get('instagram_nick'),
                client_project_info=user_dict.get('client_project_info'),
                lead_status=user_dict.get('lead_status', 'new'),
            )
            self.session.add(obj)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при добавления пользователя: {e}")
            return False

    async def get_user(self, tg_id: int) -> Optional[ClientModel]:
        try:
            result = await self.session.execute(
                select(Users).where(Users.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()
            return to_client_model(user)
        except Exception as e:
            self.logger.error(f"Ошибка при получении пользователя {tg_id}: {e}")
            return None

    async def get_all_users(self) -> List[ClientModel]:
        try:
            result = await self.session.execute(select(Users))
            users = result.scalars().all()
            return [to_client_model(u) for u in users if to_client_model(u)]
        except Exception as e:
            self.logger.error(f"Ошибка при получении всех пользователей: {e}")
            return []

    async def user_exists(self, tg_id: int) -> bool:
        try:
            result = await self.session.execute(
                select(Users.tg_id).where(Users.tg_id == tg_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            self.logger.error(f"Ошибка при проверке существования пользователя {tg_id}: {e}")
            return False

    async def count_users(self) -> int:
        try:
            result = await self.session.execute(
                select(func.count()).select_from(Users)
            )
            return result.scalar_one()
        except Exception as e:
            self.logger.error(f"Ошибка при подсчете пользователей: {e}")
            return 0

    async def update_user_fields(self, tg_id: int, **fields) -> bool:
        if not fields:
            return False
        try:
            await self.session.execute(
                update(Users).where(Users.tg_id == tg_id).values(**fields)
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении пользователя {tg_id}: {e}")
            return False

    async def update_lead_status(self, tg_id: int, new_status: str) -> bool:
        """Обновляет статус лида"""
        return await self.update_user_fields(tg_id, lead_status=new_status)

    async def add_message_to_history(
        self, 
        tg_id: int, 
        source: str, 
        content: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        try:
            result = await self.session.execute(
                select(Users).where(Users.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return False
            
            message_data = {
                "source": source,
                "content": content,
                "timestamp": (timestamp or datetime.now()).isoformat()
            }
            
            if user.message_history is None:
                user.message_history = []
            
            user.message_history.append(message_data)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении сообщения в историю для {tg_id}: {e}")
            return False

    async def get_message_history(self, tg_id: int) -> List[ClientMessage]:
        try:
            user = await self.get_user(tg_id)
            if not user:
                return []
            return user.message_history
        except Exception as e:
            self.logger.error(f"Ошибка при получении истории сообщений для {tg_id}: {e}")
            return []

    async def delete_user(self, tg_id: int) -> bool:
        try:
            await self.session.execute(
                delete(Users).where(Users.tg_id == tg_id)
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении пользователя {tg_id}: {e}")
            return False

    async def delete_all(self) -> bool:
        try:
            await self.session.execute(delete(Users))
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении всех пользователей: {e}")
            return False

    async def get_users_by_status(self, status: str) -> List[ClientModel]:
        try:
            result = await self.session.execute(
                select(Users).where(Users.lead_status == status)
            )
            users = result.scalars().all()
            return [to_client_model(u) for u in users if to_client_model(u)]
        except Exception as e:
            self.logger.error(f"Ошибка при получении пользователей по статусу {status}: {e}")
            return []

    async def update_project_info(self, tg_id: int, project_info: str) -> bool:
        return await self.update_user_fields(tg_id, client_project_info=project_info)

