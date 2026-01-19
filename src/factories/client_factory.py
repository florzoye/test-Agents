from src.enum.db import DatabaseType
from db.sqlite.crud import ClientSQL
from db.sqlalchemy.crud import ClientORM
from db.database_protocol import ClientBase

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