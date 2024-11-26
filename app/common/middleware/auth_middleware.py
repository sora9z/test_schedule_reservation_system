import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.common.auth.auth_guard import AuthGuard
from app.common.constants import UserType
from app.common.exceptions import AuthorizationError


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, guard: AuthGuard):
        super().__init__(app)
        self.guard = guard
        # Swagger 및 기타 제외 경로 추가
        self.excluded_paths = [
            "/openapi.json",
            "/docs",
            "/docs/oauth2-redirect",
            "/redoc",
            "/api/v1/users/login",
            "/api/v1/users/",
        ]

    async def dispatch(self, request, call_next):
        admin_only_pattern = re.compile(r"/api/v1/.+/admin")
        if any(route == request.url.path for route in self.excluded_paths):
            return await call_next(request)

        try:
            auth_data = await self.guard.authenticate(request)
            if admin_only_pattern.match(request.url.path):
                if auth_data["type"] != UserType.ADMIN.value:
                    raise AuthorizationError("권한이 없습니다.")

            request.state.auth = auth_data
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": str(e)})

        return await call_next(request)
