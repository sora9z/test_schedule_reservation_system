from datetime import date, datetime, time, timedelta

import pytest

from app.common.constants import ReservationStatus, UserType
from app.common.exceptions import AuthorizationError


@pytest.mark.asyncio
async def test_get_reservations_by_user_success(mock_reservation_repository, reservation_service):
    """
    [Reservation] 유저는 자신의 예약 내역을 조회할 수 있다
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    mock_reservation_repository.get_reservations.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "exam_date": exam_date,
            "exam_start_date": datetime.combine(exam_date, time(10, 0)),
            "exam_end_date": datetime.combine(exam_date, time(11, 0)),
            "applicants": 1000,
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": 2,
            "user_id": 1,
            "exam_date": exam_date,
            "exam_start_date": datetime.combine(exam_date, time(14, 0)),
            "exam_end_date": datetime.combine(exam_date, time(15, 0)),
            "applicants": 30000,
            "status": ReservationStatus.PENDING.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]
    input_data = {"user_id": 1, "type": UserType.USER.value}

    # when
    result = await reservation_service.get_reservations(**input_data)

    # then
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["exam_date"] == exam_date
    assert result[0]["exam_start_date"] == datetime.combine(exam_date, time(10, 0))
    assert result[0]["exam_end_date"] == datetime.combine(exam_date, time(11, 0))
    assert result[1]["id"] == 2
    assert result[1]["exam_date"] == exam_date
    assert result[1]["exam_start_date"] == datetime.combine(exam_date, time(14, 0))
    assert result[1]["exam_end_date"] == datetime.combine(exam_date, time(15, 0))


@pytest.mark.asyncio
async def test_get_reservations_by_admin_success(mock_reservation_repository, reservation_service):
    """
    [Reservation] 어드민은 모든 예약 내역을 조회할 수 있다
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    mock_reservation_repository.get_reservations.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "exam_date": exam_date,
            "exam_start_date": datetime.combine(exam_date, time(10, 0)),
            "exam_end_date": datetime.combine(exam_date, time(11, 0)),
            "applicants": 1000,
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": 2,
            "user_id": 2,
            "exam_date": exam_date,
            "exam_start_date": datetime.combine(exam_date, time(14, 0)),
            "exam_end_date": datetime.combine(exam_date, time(15, 0)),
            "applicants": 30000,
            "status": ReservationStatus.PENDING.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]
    input_data = {"user_id": 1, "type": UserType.ADMIN.value}

    # when
    result = await reservation_service.get_reservations(**input_data)

    # then
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["user_id"] == 1
    assert result[1]["id"] == 2
    assert result[1]["user_id"] == 2


@pytest.mark.asyncio
async def test_get_reservations_by_user_fail(mock_reservation_repository, reservation_service):
    """
    [Reservation] 유저는 다른 유저의 예약 내역을 조회할 수 없다(권한 없음 에러 발생)
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    mock_reservation_repository.get_reservations.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "exam_date": exam_date,
            "exam_start_date": datetime.combine(exam_date, time(10, 0)),
            "exam_end_date": datetime.combine(exam_date, time(11, 0)),
            "applicants": 1000,
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": 2,
            "user_id": 2,
            "exam_date": exam_date,
            "exam_start_date": datetime.combine(exam_date, time(14, 0)),
            "exam_end_date": datetime.combine(exam_date, time(15, 0)),
            "applicants": 30000,
            "status": ReservationStatus.PENDING.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]
    input_data = {"user_id": 1, "type": UserType.USER.value}

    # when
    with pytest.raises(AuthorizationError) as e:
        await reservation_service.get_reservations(**input_data)

    # then
    assert isinstance(e.value, AuthorizationError)


@pytest.mark.asyncio
async def test_get_reservations_by_admin_fail(mock_reservation_repository, reservation_service):
    """
    [Reservation] 예약 내역이 없다면 빈 배열을 반환한다
    """
    # given
    input_data = {"user_id": 1, "type": UserType.ADMIN.value}
    mock_reservation_repository.get_reservations.return_value = []

    # when
    result = await reservation_service.get_reservations(**input_data)

    # then
    assert result == []
