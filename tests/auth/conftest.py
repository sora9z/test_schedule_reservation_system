import hashlib
from unittest.mock import MagicMock

import pytest

from app.common.auth.jwt_service import JWTService
from app.common.database.models.reservation import Reservation
from app.common.database.models.slot import Slot
from app.common.database.models.user import User
from app.common.respository.user_repository import AuthRepository
from app.config import Config
from app.services.auth_service import AuthService


@pytest.fixture
def mock_auth_repository(mocker):
    return mocker.Mock(spec=AuthRepository)


@pytest.fixture
def mock_user(mocker):
    def _mock_user(type):
        mock_user = MagicMock(spec=User)
        mock_user.configure_mock(
            id=1,
            type=type,
            email="grep@grep.com",
            hashed_password=hashlib.sha256("password".encode()).hexdigest(),
            reservations=[MagicMock(spec=Reservation)],
        )
        return mock_user

    return _mock_user


@pytest.fixture
def mock_slot(mocker):
    return mocker.Mock(spec=Slot)


@pytest.fixture
def mock_reservation(mocker):
    def _mock_reservation(reservation_id):
        mock_reservation = mocker.Mock(spec=Reservation)
        mock_reservation.id = reservation_id
        mock_reservation.slots = []
        return mock_reservation

    return _mock_reservation


@pytest.fixture
def mock_settings(mocker):
    return mocker.Mock(spec=Config)


@pytest.fixture
def mock_jwt_service(mocker):
    return mocker.Mock(spec=JWTService)


@pytest.fixture
def auth_service(mock_auth_repository, mock_settings, mock_jwt_service):
    return AuthService(repository=mock_auth_repository, settings=mock_settings, jwt_service=mock_jwt_service)
