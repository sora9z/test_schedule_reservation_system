from fastapi import Request

from app.common.exceptions import AuthenticationError


def get_current_user(request: Request):
    user_info = request.state.auth
    if not user_info:
        raise AuthenticationError("인증 정보가 없습니다.")
    return user_info
