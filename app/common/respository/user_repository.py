import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_scoped_session

from app.common.database.models.user import User

logger = logging.getLogger(__name__)


class AuthRepository:
    def __init__(self, session_factory: async_scoped_session) -> None:
        self.session_factory = session_factory

    async def get_user_by_email(self, email: str) -> User | None:
        try:
            async with self.session_factory() as session:
                user = await session.scalar(select(User).where(User.email == email))
            return user
        except Exception as e:
            logger.error(f"[user_repository] get_user_by_email error: {e}")
            raise e

    async def create_user(self, user: User) -> User:
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()
            return user
