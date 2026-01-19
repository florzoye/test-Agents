import logging
from data.init_configs import DB_CONFIG

from db.database_protocol import ClientBase
from db.sqlite.manager import AsyncDatabaseManager
from db.sqlalchemy.session import SQLAlchemyManager
from src.utils.factrory import ClientFactory, DatabaseType

class Database:
    """Менеджер базы данных"""
    def __init__(self):
        self.repo: ClientBase = None
        self.sqlite_manager: AsyncDatabaseManager = None
        self.sqlalchemy_manager: SQLAlchemyManager = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def setup(self):
        if DB_CONFIG.DB_TYPE == "sqlite":
            self.sqlite_manager = AsyncDatabaseManager(DB_CONFIG.SQLITE_PATH)
            await self.sqlite_manager.connect()
            
            self.repo: ClientBase = ClientFactory.create(
                DatabaseType.SQLITE, 
                self.sqlite_manager
            )
            await self.repo.create_tables()
            self.logger.info(f"✅ SQLite подключена: {DB_CONFIG.SQLITE_PATH}")
        else:
            self.sqlalchemy_manager = SQLAlchemyManager()
            self.sqlalchemy_manager.init()

            session = self.sqlalchemy_manager.get_session()

            self.repo: ClientBase = ClientFactory.create(
                DatabaseType.SQLALCHEMY, 
                session
            )

            db_url = DB_CONFIG.url
            safe_url = db_url.split('@')[1] if '@' in db_url else db_url
            self.logger.info(f"✅ PostgreSQL подключена: {safe_url}")
    
    def get(self) -> ClientBase:
        """Получить репозиторий клиентов"""
        if self.repo is None:
            raise RuntimeError(
                "Database not initialized. Call database.setup() first"
            )
        return self.repo
    
    async def close(self):
        """Закрыть соединение с БД"""
        if self.sqlite_manager:
            await self.sqlite_manager.close()
            self.logger.info("✅ SQLite соединение закрыто")
        
        if self.sqlalchemy_manager:
            await self.sqlalchemy_manager.close()
            self.logger.info("✅ SQLAlchemy соединение закрыто")


database = Database()