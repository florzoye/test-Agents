from typing import AsyncIterator
from contextlib import asynccontextmanager
from data.configs.db_config import db_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class SQLAlchemyManager:
    def __init__(self):
        self.engine = None
        self.session_maker = None
    
    def init(self):
        if self.engine is not None:
            return  
        
        database_url = db_config.url
        
        self.engine = create_async_engine(
            database_url,
            echo=db_config.DB_DEBUG,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        if self.session_maker is None:
            raise RuntimeError(
                "SQLAlchemy не инициализирована, сначала вызови init()"
            )

        session: AsyncSession = self.session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def get_engine(self):
        if self.engine is None:
            raise RuntimeError(
                "SQLAlchemy не инициализирована, для начала init()"
            )
        return self.engine


sqlalchemy_manager = SQLAlchemyManager()