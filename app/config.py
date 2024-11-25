# BaseSetting useage: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#installation
# https://docs.pydantic.dev/latest/concepts/fields/
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # database
    DATABASE_USER: str = Field(default="grep_user", env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field(default="password", env="DATABASE_PASSWORD")
    DATABASE_HOST: str = Field(default="localhost", env="DATABASE_HOST")
    DATABASE_PORT: str = Field(default="5432", env="DATABASE_PORT")
    DATABASE_NAME: str = Field(default="grep_db", env="DATABASE_NAME")

    @property
    def DATABASE_URL(self) -> str:
        return f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


settings = Config(_env_file=".env", _env_file_encoding="utf-8")
