import logging

from fastapi import Request

from app.common.auth.jwt_service import JWTService
from app.common.auth.strategies.base_strategy import AuthStrategy
from app.common.exceptions import JwtError

logger = logging.getLogger(__name__)


class JWTAuthStrategy(AuthStrategy):
    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service

    async def authenticate(self, request: Request) -> dict:
        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise JwtError("Authorization 헤더가 없습니다.")

        token = auth_header.split(" ")[1]
        try:
            decoded_data = self.jwt_service.verify_token(token)
            return {
                "user_id": decoded_data.get("sub"),
                "type": decoded_data.get("type"),
            }
        except Exception as e:
            logger.error(f"JWT 인증 실패: {e}")
            raise JwtError(str(e))
