from langchain.agents import create_agent
from langchain_classic.tools import BaseTool
from langchain.messages import SystemMessage
from langchain_core.runnables import Runnable

from src.enum.db import DatabaseType
from src.core.agents.models.base import BaseLLM

from db.sqlite.crud import ClientSQL
from db.sqlalchemy.crud import ClientORM
from db.database_protocol import ClientBase
from data.init_configs import MIDDLEWARE_SERVICE


class AgentFactory:
    async def lc_create_agent(
        self,
        llm: BaseLLM,
        tools: list[BaseTool],
        system_prompt: SystemMessage
    ) -> Runnable:
        llm_instance = await llm.get_llm()
        agent = create_agent(
            model=llm_instance,
            tools=tools,
            system_prompt=system_prompt,
            middleware=MIDDLEWARE_SERVICE.middlewares,
        )

        return agent

class ClientFactory:
    @staticmethod
    def create(db_type: DatabaseType, connection) -> ClientBase:
        """
        Создает репозиторий клиентов в зависимости от типа БД
        
        Args:
            db_type: Тип базы данных
            connection: Подключение к БД (AsyncDatabaseManager или AsyncSession)
            
        Returns:
            Экземпляр ClientBase (ClientSQL или ClientORM)
        """
        if db_type == DatabaseType.SQLITE:
            return ClientSQL(connection)
        elif db_type == DatabaseType.SQLALCHEMY:
            return ClientORM(connection)
        else:
            raise ValueError(f"Неподдерживаемый тип базы данных: {db_type}")