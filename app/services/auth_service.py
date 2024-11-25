import hashlib
import logging

from app.common.database.models.user import User
from app.common.exceptions import DuplicateError
from app.common.respository.user_repository import AuthRepository
from app.schemas.user_schema import UserCreateRequest, UserCreateResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def create_user(self, data: UserCreateRequest) -> UserCreateResponse:
        try:
            print("뭐지", data)
            existing_user = await self.repository.get_user_by_email(data.email)
            if existing_user:
                raise DuplicateError("이미 존재하는 이메일입니다.")

            user = User(
                email=data.email,
                hashed_password=self._hash_password(data.password),
                type=data.type,
            )

            user = await self.repository.create_user(user=user)
            return UserCreateResponse.model_validate(user)
        except Exception as e:
            logger.error(f"[user/auth_service] create_user error: {e}")
            raise e

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
