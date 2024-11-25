# about engine: https://docs.sqlalchemy.org/en/20/core/engines.html
# postgresql dialet : https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
# about session: https://docs.sqlalchemy.org/en/20/orm/session_basics.html#what-does-the-session-do
# async engine : https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncEngine
# async session : https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncSession

import logging
from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import psycopg
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_url: str) -> None:

        # dialect+driver://username:password@host:port/database
        self.async_engine = create_async_engine(f"postgresql+psycopg://{database_url}", pool_pre_ping=True, echo=True)

        self.async_session = async_scoped_session(
            async_sessionmaker(
                self.async_engine,
                expire_on_commit=False,
                autoflush=False,
                future=True,
            ),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self.async_session()
        try:
            yield session
        except psycopg.IntegrityError as exception:
            logger.error("Session rollback : %s", exception)
            await session.rollback()
        finally:
            await session.close()
