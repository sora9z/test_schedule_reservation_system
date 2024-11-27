# https://docs.pytest.org/en/stable/how-to/fixtures.html
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database.models.reservation import Reservation
from app.common.database.models.slot import Slot
from app.config import Config
from app.services.reservation_service import ReservationService


@pytest.fixture
def mock_reservation_repository(mocker):
    repository = mocker.Mock()
    repository.create_reservation_with_external_session = mocker.AsyncMock()
    repository.get_reservations_by_user_id = mocker.AsyncMock()
    repository.get_reservations = mocker.AsyncMock()
    repository.get_reservation_by_id_with_external_session = mocker.AsyncMock()
    repository.update_reservation_with_external_session = mocker.AsyncMock()
    return repository


@pytest.fixture
def mock_slot_repository(mocker):
    repository = mocker.Mock()
    repository.get_overlapping_slots_with_external_session = mocker.AsyncMock()
    repository.get_available_slots = mocker.AsyncMock()
    return repository


@pytest.fixture
def mock_reservation(mocker):
    def _mock_reservation(reservation_id, user_id, exam_date, start_time, end_time, applicants, status):
        mock_res = mocker.AsyncMock(spec=Reservation)
        mock_res.id = reservation_id
        mock_res.user_id = user_id
        mock_res.exam_date = exam_date
        mock_res.exam_start_time = start_time
        mock_res.exam_end_time = end_time
        mock_res.applicants = applicants
        mock_res.status = status
        mock_res.slots = []
        return mock_res

    return _mock_reservation


@pytest.fixture
def mock_slot(mocker):
    def _mock_slot(slot_id, exam_date, start_time, end_time, remaining_capacity):
        mock_slt = mocker.AsyncMock(spec=Slot)
        mock_slt.id = slot_id
        mock_slt.exam_date = exam_date
        mock_slt.exam_start_time = start_time
        mock_slt.exam_end_time = end_time
        mock_slt.remaining_capacity = remaining_capacity
        return mock_slt

    return _mock_slot


@pytest.fixture
def mock_settings(mocker):
    mock_settings = mocker.Mock(spec=Config)
    mock_settings.MAX_APPLICANTS = 50000
    return mock_settings


@pytest.fixture
def mock_session_factory(mocker):
    mock_session = mocker.AsyncMock(spec=AsyncSession)
    mock_session.add = mocker.AsyncMock()
    mock_session.commit = mocker.AsyncMock()

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
