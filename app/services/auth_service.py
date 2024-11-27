import hashlib
import logging

from app.common.auth.jwt_service import JWTService
from app.common.database.models.user import User
from app.common.exceptions import AuthenticationError, DuplicateError
from app.common.respository.user_repository import AuthRepository
from app.config import Config
from app.schemas.user_schema import UserCreateRequest, UserCreateResponse, UserLoginRequest, UserLoginResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: AuthRepository, settings: Config, jwt_service: JWTService) -> None:
        self.repository = repository
        self.settings = settings
        self.jwt_service = jwt_service

    async def create_user(self, data: UserCreateRequest) -> UserCreateResponse:
        try:
            await self._validate_create_user(data)

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

    async def _validate_create_user(self, data):
        existing_user = await self.repository.get_user_by_email(data.email)
        if existing_user:
            raise DuplicateError("이미 존재하는 이메일입니다.")

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    async def login(self, data: UserLoginRequest) -> UserLoginResponse:
        try:
            user = await self._validate_login(data)

            access_token = self.jwt_service.create_access_token(
                data={"user_id": user.id, "type": str(user.type)},
            )
            refresh_token = self.jwt_service.create_refresh_token(
                data={"user_id": user.id, "type": str(user.type)},
            )
            return UserLoginResponse(access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            logger.error(f"[user/auth_service] login error: {e}")
            raise e

    async def _validate_login(self, data):
        user = await self.repository.get_user_by_email(data.email)
        if not user:
            raise AuthenticationError("인증되지 않은 사용자입니다.")

        if user.hashed_password != self._hash_password(data.password):
            raise AuthenticationError("인증되지 않은 사용자입니다.")
        return user
