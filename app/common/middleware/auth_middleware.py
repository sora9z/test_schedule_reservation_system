from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.common.auth.auth_guard import AuthGuard


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
            "/api/v1/users/signup",
        ]

    async def dispatch(self, request, call_next):
        if any(route == request.url.path for route in self.excluded_paths):
            return await call_next(request)

        try:
            auth_data = await self.guard.authenticate(request)
            request.state.auth = auth_data
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": str(e)})

        return await call_next(request)
