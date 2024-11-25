# BaseSetting useage: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#installation
# https://docs.pydantic.dev/latest/concepts/fields/
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # database
    DATABASE_USER: str = Field(default="grep_user", json_schema_extra={"env": "DATABASE_USER"})
    DATABASE_PASSWORD: str = Field(default="password", json_schema_extra={"env": "DATABASE_PASSWORD"})
    DATABASE_HOST: str = Field(default="localhost", json_schema_extra={"env": "DATABASE_HOST"})
    DATABASE_PORT: str = Field(default="5432", json_schema_extra={"env": "DATABASE_PORT"})
    DATABASE_NAME: str = Field(default="grep_db", json_schema_extra={"env": "DATABASE_NAME"})

    # jwt
    JWT_SECRET_KEY: str = Field(default="secret", json_schema_extra={"env": "JWT_SECRET_KEY"})
    JWT_ALGORITHM: str = Field(default="HS256", json_schema_extra={"env": "JWT_ALGORITHM"})
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_MINUTES"})
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=60, json_schema_extra={"env": "REFRESH_TOKEN_EXPIRE_MINUTES"})

    @property
    def DATABASE_URL(self) -> str:
        return f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


settings = Config(_env_file=".env", _env_file_encoding="utf-8")
