import json
import logging
from datetime import datetime
from typing import List, Optional

from db.sqlite.manager import AsyncDatabaseManager
from db.sqlite.schemas import (
    create_clients_table_sql,
    insert_client_sql,
    select_client_sql,
    select_all_clients_sql,
    delete_client_sql,
    delete_all_clients_sql,
    client_exists_sql,
    select_clients_by_status_sql,
    select_message_history_sql,
)

from src.models.messages import BaseMessage
from db.database_protocol import ClientBase
from src.models.client_model import ClientModel, to_client_model


class ClientSQL(ClientBase):
    def __init__(self, db: AsyncDatabaseManager):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_tables(self) -> bool:
        try:
            await self.db.execute(create_clients_table_sql())
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при создании таблиц: {e}")
            return False

    async def add_client(self, client: ClientModel) -> bool:
        try:
            message_history = []
            for msg in client.message_history:
                timestamp = msg.timestamp
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.isoformat()
                elif timestamp is None:
                    timestamp = datetime.now().isoformat()
                
                message_history.append({
                    "source": msg.source,
                    "content": msg.content,
                    "timestamp": timestamp
                })
            
            await self.db.execute(insert_client_sql(), {
                "tg_id": client.tg_id,
                "message_history": json.dumps(message_history),
                "age": client.age,
                "full_name": client.full_name or "",
                "username": client.username or "",
                "email": client.email or "",
                "tg_nick": client.tg_nick or "",
                "client_project_info": client.client_project_info or "",
                "lead_status": client.lead_status or "new",
            })
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении клиента: {e}", exc_info=True)
            return False

    async def get_client(self, tg_id: int) -> Optional[ClientModel]:
        try:
            row = await self.db.fetchone(select_client_sql(), {"tg_id": tg_id})
            if not row:
                return None
            
            if row.get("message_history"):
                row["message_history"] = json.loads(row["message_history"])
            
            return to_client_model(row)
        except Exception as e:
            self.logger.error(f"Ошибка при получении клиента {tg_id}: {e}")
            return None

    async def get_all_client(self) -> List[ClientModel]:
        try:
            rows = await self.db.fetchall(select_all_clients_sql())
            clients = []
            for row in rows:
                if row.get("message_history"):
                    row["message_history"] = json.loads(row["message_history"])
                client = to_client_model(row)
                if client:
                    clients.append(client)
            return clients
        except Exception as e:
            self.logger.error(f"Ошибка при получении всех клиентов: {e}")
            return []

    async def client_exists(self, tg_id: int) -> bool:
        try:
            row = await self.db.fetchone(client_exists_sql(), {"tg_id": tg_id})
            return row is not None
        except Exception as e:
            self.logger.error(f"Ошибка при проверке существования клиента {tg_id}: {e}")
            return False

    async def update_client_fields(self, tg_id: int, **fields) -> bool:
        try:
            if not fields:
                return False

            if "message_history" in fields and isinstance(fields["message_history"], list):
                fields["message_history"] = json.dumps(fields["message_history"])

            set_clause = ", ".join(f"{k} = :{k}" for k in fields)
            sql = f"UPDATE clients SET {set_clause} WHERE tg_id = :tg_id"
            fields["tg_id"] = tg_id
            await self.db.execute(sql, fields)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении клиента {tg_id}: {e}")
            return False

    async def update_lead_status(self, tg_id: int, new_status: str) -> bool:
        return await self.update_client_fields(tg_id, lead_status=new_status)

    async def update_project_info(self, tg_id: int, project_info: str) -> bool:
        return await self.update_client_fields(tg_id, client_project_info=project_info)

    async def update_message_history(
        self, 
        tg_id: int, 
        source: str, 
        content: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        try:
            row = await self.db.fetchone(
                select_message_history_sql(), 
                {"tg_id": tg_id}
            )
            
            if not row:
                self.logger.warning(f"Клиент {tg_id} не найден")
                return False
            
            message_history = []
            if row.get("message_history"):
                message_history = json.loads(row["message_history"])
            
            message_data = {
                "source": source,
                "content": content,
                "timestamp": (timestamp or datetime.now()).isoformat()
            }
            message_history.append(message_data)
            
            await self.update_client_fields(tg_id, message_history=message_history)
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
            await self.db.execute(delete_client_sql(), {"tg_id": tg_id})
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении клиента {tg_id}: {e}")
            return False

    async def delete_all(self) -> bool:
        try:
            await self.db.execute(delete_all_clients_sql())
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении всех клиентов: {e}")
            return False

    async def delete_all_tables(self) -> bool:
        """Удаляет все таблицы"""
        try:
            await self.db.execute("DROP TABLE IF EXISTS clients")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении таблиц: {e}")
            return False

    async def get_clients_by_status(self, status: str) -> List[ClientModel]:
        try:
            rows = await self.db.fetchall(
                select_clients_by_status_sql(), 
                {"status": status}
            )
            clients = []
            for row in rows:
                if row.get("message_history"):
                    row["message_history"] = json.loads(row["message_history"])
                client = to_client_model(row)
                if client:
                    clients.append(client)
            return clients
        except Exception as e:
            self.logger.error(f"Ошибка при получении клиентов по статусу {status}: {e}")
            return []