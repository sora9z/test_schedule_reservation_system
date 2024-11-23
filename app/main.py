from fastapi import FastAPI

from app.container import Container

# app = FastAPI(title="Test Schedule Resesrvation System")


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(title="Test Schedule Resesrvation System")
    app.container = container
    return app


# @app.get("/")
# def read_root():
#     return {"message": "Hello World"}

app = create_app()
