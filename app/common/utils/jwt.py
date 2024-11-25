from datetime import datetime, timedelta

import jwt

from app.common.exceptions import AuthenticationError


def create_access_token(data: dict, expires_delta: int = None, secret_key: str = None, algorithm: str = None):
    expires_delta = expires_delta or 60
    secret_key = secret_key or "default_secret_key"
    algorithm = algorithm or "HS256"
    return _creat_token(data, expires_delta, secret_key, algorithm)


def create_refresh_token(data: dict, expires_delta: int = None, secret_key: str = None, algorithm: str = None):
    expires_delta = expires_delta or 7
    secret_key = secret_key or "default_secret_key"
    algorithm = algorithm or "HS256"
    return _creat_token(data, expires_delta, secret_key, algorithm)


def _creat_token(data: dict, expires_delta: int, secret_key: str, algorithm: str):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_token(token: str, secret_key: str, algorithm: str):
    try:
        decoded_data = jwt.decode(token, key=secret_key, algorithms=[algorithm])
        return decoded_data
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("토큰이 만료되었습니다.")
    except jwt.PyJWTError:
        raise AuthenticationError("인증되지 않은 사용자입니다.")
