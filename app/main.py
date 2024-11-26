from fastapi import Depends, FastAPI
from fastapi.security import APIKeyHeader

from app.api import api
from app.common.middleware.auth_middleware import AuthMiddleware
from app.container import Container

app_container_modules = [
    "app.api.routes.v1.user_api",
    "app.api.routes.v1.reservation_api",
]


def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=app_container_modules)
    # swagger에 헤더 추가
    auth_header = APIKeyHeader(name="Authorization", auto_error=False)
    app = FastAPI(title="Test Schedule Resesrvation System", dependencies=[Depends(auth_header)])
    app.container = container
    app.include_router(api.router)

    # middleware 등록

    auth_guard = container.auth_guard()
    app.add_middleware(AuthMiddleware, guard=auth_guard)
    return app


app = create_app()
