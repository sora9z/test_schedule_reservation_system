import pytest

from app.common.respository.reservation_repository import ReservationRepository
from app.config import Config
from app.services.reservation_service import ReservationService


@pytest.fixture
def mock_reservation_repository(mocker):
    return mocker.Mock(spec=ReservationRepository)


@pytest.fixture
def reservation_service(mock_reservation_repository, mock_settings):
    return ReservationService(repository=mock_reservation_repository, settings=mock_settings)


@pytest.fixture
def mock_settings(mocker):
    return mocker.Mock(spec=Config)
