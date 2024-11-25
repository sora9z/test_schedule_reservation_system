from fastapi import FastAPI

from app.api import api
from app.container import Container

app_container_modules = [
    "app.api.routes.v1.user_api",
]


def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=app_container_modules)
    app = FastAPI(title="Test Schedule Resesrvation System")
    app.container = container
    app.include_router(api.router)
    return app


app = create_app()
