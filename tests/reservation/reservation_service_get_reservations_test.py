from datetime import date, datetime, time, timedelta

import pytest

from app.common.constants import ReservationStatus, UserType
from app.common.exceptions import AuthorizationError


@pytest.mark.asyncio
async def test_get_reservations_by_user_id_success(mock_reservation_repository, reservation_service):
    """
    [Reservation] 유저는 자신의 예약 내역을 조회할 수 있다
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    mock_reservation_repository.get_reservations_by_user_id.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "exam_date": exam_date,
            "exam_start_time": time(10, 0),
            "exam_end_time": time(11, 0),
            "applicants": 1000,
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": 2,
            "user_id": 1,
            "exam_date": exam_date,
            "exam_start_time": time(14, 0),
            "exam_end_time": time(15, 0),
            "applicants": 30000,
            "status": ReservationStatus.PENDING.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]

    # when
    result = await reservation_service.get_reservations_by_user(user_id=1)

    # then
    assert len(result.reservations) == 2
    assert result.reservations[0].id == 1
    assert result.reservations[1].id == 2


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
            "exam_start_time": time(10, 0),
            "exam_end_time": time(11, 0),
            "applicants": 1000,
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": 2,
            "user_id": 2,
            "exam_date": exam_date,
            "exam_start_time": time(14, 0),
            "exam_end_time": time(15, 0),
            "applicants": 30000,
            "status": ReservationStatus.PENDING.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]

    # when
    result = await reservation_service.get_reservations_by_admin(user_type=UserType.ADMIN)

    # then
    assert len(result.reservations) == 2
    assert result.reservations[0].id == 1
    assert result.reservations[0].user_id == 1
    assert result.reservations[1].id == 2
    assert result.reservations[1].user_id == 2


@pytest.mark.asyncio
async def test_get_reservations_by_admin_fail(mock_reservation_repository, reservation_service):
    """
    [Reservation] 어드민이 아닌 유저는 다른 유저의 예약 내역을 조회할 수 없다(권한 없음 에러 발생)
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    mock_reservation_repository.get_reservations_by_admin.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "exam_date": exam_date,
            "exam_start_time": datetime.combine(exam_date, time(10, 0)),
            "exam_end_time": datetime.combine(exam_date, time(11, 0)),
            "applicants": 1000,
            "status": ReservationStatus.CONFIRMED.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": 2,
            "user_id": 2,
            "exam_date": exam_date,
            "exam_start_time": datetime.combine(exam_date, time(14, 0)),
            "exam_end_time": datetime.combine(exam_date, time(15, 0)),
            "applicants": 30000,
            "status": ReservationStatus.PENDING.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]

    # when
    with pytest.raises(AuthorizationError) as e:
        await reservation_service.get_reservations_by_admin(user_type=UserType.USER)

    # then
    assert isinstance(e.value, AuthorizationError)


@pytest.mark.asyncio
async def test_get_reservations_by_admin_success_empty(mock_reservation_repository, reservation_service):
    """
    [Reservation] 예약 내역이 없다면 빈 배열을 반환한다
    """
    # given
    mock_reservation_repository.get_reservations.return_value = []

    # when
    result = await reservation_service.get_reservations_by_admin(user_type=UserType.ADMIN)

    # then
    assert result.reservations == []
