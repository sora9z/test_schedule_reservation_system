from fastapi import status


class DuplicateError(Exception):
    """데이터 중복 시 발생하는 예외"""

    def __init__(self, message: str):
        self.message = message
        self.status_code = status.HTTP_409_CONFLICT


class NotFoundError(Exception):
    """데이터 존재하지 않을 때 발생하는 예외"""

    def __init__(self, message: str):
        self.message = message
        self.status_code = status.HTTP_404_NOT_FOUND


class AuthenticationError(Exception):
    """인증 실패 시 발생하는 예외"""

    def __init__(self, message: str):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED


class JwtError(Exception):
    """JWT 오류 시 발생하는 예외"""

    def __init__(self, message: str):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED


class BadRequestError(Exception):
    """잘못된 요청 시 발생하는 예외"""

    def __init__(self, message: str):
        self.message = message
        self.status_code = status.HTTP_400_BAD_REQUEST
