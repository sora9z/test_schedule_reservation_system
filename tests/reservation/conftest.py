# https://docs.pytest.org/en/stable/how-to/fixtures.html
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.services.reservation_service import ReservationService


@pytest.fixture
def mock_reservation_repository(mocker):
    repository = mocker.Mock()
    repository.get_overlapping_reservations_with_external_session = mocker.AsyncMock()
    repository.create_reservation_with_external_session = mocker.AsyncMock()
    return repository


@pytest.fixture
def mock_slot_repository(mocker):
    repository = mocker.Mock()
    repository.get_overlapping_slots_with_external_session = mocker.AsyncMock()
    repository.get_available_slots = mocker.AsyncMock()
    return repository


@pytest.fixture
def mock_settings(mocker):
    mock_settings = mocker.Mock(spec=Config)
    mock_settings.MAX_APPLICANTS = 50000
    return mock_settings


@pytest.fixture
def mock_session_factory(mocker):
    mock_session = mocker.AsyncMock(spec=AsyncSession)

    class MockTransaction:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockSessionContextManager:
        async def __aenter__(self):
            return mock_session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        def begin(self):
            return MockTransaction()

    mock_session_factory = mocker.Mock()
    mock_session_factory.return_value = MockSessionContextManager()

    return mock_session_factory


@pytest.fixture
def reservation_service(
    mock_reservation_repository,
    mock_slot_repository,
    mock_settings,
    mock_session_factory,
):
    return ReservationService(
        repository=mock_reservation_repository,
        slot_repository=mock_slot_repository,
        settings=mock_settings,
        session_factory=mock_session_factory,
    )
