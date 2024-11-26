from datetime import datetime, timedelta

import jwt

from app.common.exceptions import AuthenticationError


class JWTService:
    def __init__(self, settings):
        self.settings = settings

    def create_access_token(self, data: dict):
        return self._create_token(data, expire=datetime.now() + timedelta(minutes=60))

    def create_refresh_token(self, data: dict):
        return self._create_token(data, expire=datetime.now() + timedelta(days=7))

    def _create_token(self, data: dict, expire: datetime):
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, key=self.settings.JWT_SECRET_KEY, algorithm=self.settings.JWT_ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str):
        try:
            decoded_data = jwt.decode(token, key=self.settings.JWT_SECRET_KEY, algorithms=[self.settings.JWT_ALGORITHM])
            return decoded_data
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("토큰이 만료되었습니다.")
        except jwt.PyJWTError:
            raise AuthenticationError("인증되지 않은 사용자입니다.")
