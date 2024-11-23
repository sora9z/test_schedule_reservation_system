# https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.htm
# configuration by pydantic : https://python-dependency-injector.ets-labs.org/api/providers.html#dependency_injector.providers.Configuration.from_pydantic
import json

from dependency_injector import containers, providers

from app.common.database.database import Database
from app.config import Config


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Gateways
    db = providers.Singleton(Database, db_url=config.DATABASE_URL)

    # Repositories

    # Services


container = Container()
# Config 인스턴스 생성 및 JSON 문자열로 변환
json_config = json.dumps(Config().model_dump(mode="json"))
# 동일 이슈로 인해 아래와같이 로드함 https://github.com/ets-labs/python-dependency-injector/issues/755
container.config.from_json(json_config)
