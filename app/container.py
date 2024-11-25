# https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.htm
# configuration by pydantic : https://python-dependency-injector.ets-labs.org/api/providers.html#dependency_injector.providers.Configuration.from_pydantic
import json

from dependency_injector import containers, providers

from app.common.database.database import Database
from app.common.respository.user_repository import AuthRepository
from app.config import Config
from app.services.auth_service import AuthService

config_instance = Config()
json_config = json.dumps(config_instance.model_dump(mode="json"))


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    # 동일 이슈로 인해 아래와같이 로드함 https://github.com/ets-labs/python-dependency-injector/issues/755
    config.from_json(json_config)

    database_url = config_instance.DATABASE_URL
    # Gateways
    db = providers.Singleton(Database, database_url=database_url)

    # Repositories
    auth_repository = providers.Factory(AuthRepository, session_factory=db.provided.get_session)

    # Services
    auth_service = providers.Factory(AuthService, repository=auth_repository)


container = Container()
