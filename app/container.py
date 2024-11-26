# https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.htm
# configuration by pydantic : https://python-dependency-injector.ets-labs.org/api/providers.html#dependency_injector.providers.Configuration.from_pydantic
import json

from dependency_injector import containers, providers

from app.common.auth.auth_guard import AuthGuard
from app.common.auth.jwt_service import JWTService
from app.common.auth.strategies.jwt_strategy import JWTAuthStrategy
from app.common.database.database import Database
from app.common.respository.reservation_repository import ReservationRepository
from app.common.respository.slot_repository import SlotRepository
from app.common.respository.user_repository import AuthRepository
from app.config import Config
from app.services.auth_service import AuthService
from app.services.reservation_service import ReservationService

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
    reservation_repository = providers.Factory(ReservationRepository, session_factory=db.provided.get_session)
    slot_repository = providers.Factory(SlotRepository, session_factory=db.provided.get_session)
    # Services
    auth_service = providers.Factory(AuthService, repository=auth_repository, settings=config_instance)
    reservation_service = providers.Factory(
        ReservationService,
        repository=reservation_repository,
        slot_repository=slot_repository,
        settings=config_instance,
        session_factory=db.provided.get_session,
    )

    # JWT Service
    jwt_service = providers.Singleton(JWTService, settings=config_instance)
    # Authentication Strategy
    jwt_auth_strategy = providers.Singleton(JWTAuthStrategy, jwt_service=jwt_service)
    # Authentication Guard
    auth_guard = providers.Singleton(AuthGuard, strategy=jwt_auth_strategy)


container = Container()
