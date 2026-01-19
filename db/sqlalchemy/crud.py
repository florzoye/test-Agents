import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from db.sqlalchemy.models import Base
from db.database_protocol import ClientBase
from src.models.messages import BaseMessage
from src.models.client_model import ClientModel, to_client_model

class ClientORM(ClientBase):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def create_tables(self) -> bool:
        try:
            async with self.session.begin():
                await self.session.run_sync(Base.metadata.create_all)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при создании таблиц: {e}", exc_info=True)
            return False

    async def add_client(self, client: ClientModel) -> bool:
        try:
            client_dict = client.model_dump()
            
            message_history = []
            for msg in client_dict.get('message_history', []):
                if isinstance(msg, dict):
                    timestamp = msg.get('timestamp')
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.isoformat()
                    elif timestamp is None:
                        timestamp = datetime.now().isoformat()
                    
                    message_history.append({
                        "source": msg.get('source', ''),
                        "content": msg.get('content', ''),
                        "timestamp": timestamp
                    })
                else:
                    timestamp = msg.timestamp
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.isoformat()
                    
                    message_history.append({
                        "source": msg.source,
                        "content": msg.content,
                        "timestamp": timestamp
                    })
            
            obj = ClientModel(
                tg_id=client_dict.get('tg_id'),
                message_history=message_history,
                age=client_dict.get('age'),
                full_name=client_dict.get('full_name', ''),
                username=client_dict.get('username', ''),
                email=client_dict.get('email', ''),
                tg_nick=client_dict.get('tg_nick', ''),
                client_project_info=client_dict.get('client_project_info', ''),
                lead_status=client_dict.get('lead_status', 'new'),
            )
            self.session.add(obj)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при добавления пользователя: {e}", exc_info=True)
            return False

    async def get_client(self, tg_id: int) -> Optional[ClientModel]:
        try:
            result = await self.session.execute(
                select(ClientModel).where(ClientModel.tg_id == tg_id)
            )
            client = result.scalar_one_or_none()
            return await to_client_model(client)
        except Exception as e:
            self.logger.error(f"Ошибка при получении пользователя {tg_id}: {e}")
            return None

    async def get_all_client(self) -> List[ClientModel]:
        try:
            result = await self.session.execute(select(ClientModel))
            client = result.scalars().all()
            client_models = []
            for u in client:
                client_model = await to_client_model(u)
                if client_model:
                    client_models.append(client_model)
            return client_models
        except Exception as e:
            self.logger.error(f"Ошибка при получении всех пользователей: {e}")
            return []

    async def client_exists(self, tg_id: int) -> bool:
        try:
            result = await self.session.execute(
                select(ClientModel.tg_id).where(ClientModel.tg_id == tg_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            self.logger.error(f"Ошибка при проверке существования пользователя {tg_id}: {e}")
            return False

    async def update_client_fields(self, tg_id: int, **fields) -> bool:
        if not fields:
            return False
        try:
            await self.session.execute(
                update(ClientModel).where(ClientModel.tg_id == tg_id).values(**fields)
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении пользователя {tg_id}: {e}")
            return False

    async def update_lead_status(self, tg_id: int, new_status: str) -> bool:
        """Обновляет статус лида"""
        return await self.update_client_fields(tg_id, lead_status=new_status)

    async def add_message_to_history(
        self, 
        tg_id: int, 
        source: str, 
        content: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        try:
            result = await self.session.execute(
                select(ClientModel).where(ClientModel.tg_id == tg_id)
            )
            client = result.scalar_one_or_none()
            if not client:
                self.logger.warning(f"Пользователь {tg_id} не найден")
                return False
            
            message_data = {
                "source": source,
                "content": content,
                "timestamp": (timestamp or datetime.now()).isoformat()
            }
            
            if client.message_history is None:
                client.message_history = []
            
            client.message_history.append(message_data)
            
            flag_modified(client, "message_history")
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении сообщения в историю для {tg_id}: {e}", exc_info=True)
            return False

    async def get_message_history(self, tg_id: int) -> List[BaseMessage]:
        try:
            client = await self.get_client(tg_id)
            if not client:
                return []
            return client.message_history
        except Exception as e:
            self.logger.error(f"Ошибка при получении истории сообщений для {tg_id}: {e}")
            return []

    async def delete_client(self, tg_id: int) -> bool:
        try:
            await self.session.execute(
                delete(ClientModel).where(ClientModel.tg_id == tg_id)
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении пользователя {tg_id}: {e}")
            return False

    async def delete_all(self) -> bool:
        try:
            await self.session.execute(delete(ClientModel))
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении всех пользователей: {e}")
            return False

    async def get_clients_by_status(self, status: str) -> List[ClientModel]:
        try:
            result = await self.session.execute(
                select(ClientModel).where(ClientModel.lead_status == status)
            )
            clients = result.scalars().all()
            client_models = []
            for u in clients:
                client_model = await to_client_model(u)
                if client_model:
                    client_models.append(client_model)
            return client_models
        except Exception as e:
            self.logger.error(f"Ошибка при получении пользователей по статусу {status}: {e}")
            return []

    async def update_project_info(self, tg_id: int, project_info: str) -> bool:
        return await self.update_client_fields(tg_id, client_project_info=project_info)
    
    async def update_message_history(self, tg_id: int, history: List[BaseMessage]) -> bool:
        try:
            result = await self.session.execute(
            select(ClientModel).where(ClientModel.tg_id == tg_id)
            )
            client = result.scalar_one_or_none()
            if not client:
                self.logger.warning(f"Пользователь {tg_id} не найден")
                return False

            client.message_history = [msg.model_dump() for msg in history]
            flag_modified(client, "message_history")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении истории сообщений для {tg_id}: {e}", exc_info=True)
            return False
        
    async def delete_all_tables(self) -> bool:
        try:
            async with self.session.begin():
                await self.session.run_sync(Base.metadata.drop_all)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении всех таблиц: {e}", exc_info=True)
            return False