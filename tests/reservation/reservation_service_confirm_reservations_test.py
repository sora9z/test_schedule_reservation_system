from datetime import datetime, time, timedelta

import pytest

from app.common.constants import ReservationStatus, UserType
from app.common.exceptions import AuthorizationError, BadRequestError, NotFoundError


@pytest.mark.asyncio
async def test_confirm_reservations_success(mock_reservation_repository, reservation_service):
    """
    [Reservation] 관리자는 예약을 확정정할 수 있다.
    """
    # given
    reservation_id = 1
    user_type = UserType.ADMIN

    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = {
        "id": reservation_id,
        "user_id": 1,
        "exam_date": datetime.now(),
        "exam_start_time": time(14, 0),
        "exam_end_time": time(15, 0),
        "applicants": 30000,
        "status": ReservationStatus.PENDING.value,
    }
    mock_reservation_repository.get_overlapping_slots_with_external_session.return_value = [
        {
            "id": 1,
            "exam_date": datetime.now(),
            "exam_start_time": time(14, 0),
            "exam_end_time": time(14, 30),
            "remaining_applicants": 30000,
        },
        {
            "id": 2,
            "exam_date": datetime.now(),
            "exam_start_time": time(14, 30),
            "exam_end_time": time(15, 0),
            "remaining_applicants": 50000,
        },
    ]
    mock_reservation_repository.update_slot_with_external_session.return_value = None
    mock_reservation_repository.update_reservation_status_with_external_session.return_value = None

    # when
    result = await reservation_service.confirm_reservations(reservation_id=reservation_id, user_type=user_type)

    # then
    assert result.is_success


@pytest.mark.asyncio
async def test_confirm_reservations_fail_not_admin(mock_reservation_repository, reservation_service):
    """
    [Reservation] 관리자가 아니면 예약을 확정할 수 없다(AuthorizationError)
    """
    # given
    reservation_id = 1
    user_type = UserType.USER

    # when
    with pytest.raises(AuthorizationError) as e:
        await reservation_service.confirm_reservations(reservation_id=reservation_id, user_type=user_type)

    # then
    assert isinstance(e.value, AuthorizationError)


@pytest.mark.asyncio
async def test_confirm_reservations_fail_reservation_not_found(mock_reservation_repository, reservation_service):
    """
    [Reservation] 예약이 없으면 에러를 반환한다(NotFoundError)
    """
    # given
    reservation_id = 1
    user_type = UserType.ADMIN

    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = None

    # when
    with pytest.raises(NotFoundError) as e:
        await reservation_service.confirm_reservations(reservation_id=reservation_id, user_type=user_type)

    # then
    assert isinstance(e.value, NotFoundError)


@pytest.mark.asyncio
async def test_confirm_reservations_fail_reservation_already_confirmed(
    mock_reservation_repository, reservation_service
):
    """
    [Reservation] 예약의 상태가 미확정이 아니라면 에러를 반환한다(BadRequestError)
    """
    # given
    reservation_id = 1
    user_type = UserType.ADMIN

    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = {
        "id": reservation_id,
        "user_id": 1,
        "exam_date": datetime.now(),
        "exam_start_time": time(14, 0),
        "exam_end_time": time(15, 0),
        "applicants": 30000,
        "status": ReservationStatus.CONFIRMED.value,
    }

    # when
    with pytest.raises(BadRequestError) as e:
        await reservation_service.confirm_reservations(reservation_id=reservation_id, user_type=user_type)

    # then
    assert isinstance(e.value, BadRequestError)


@pytest.mark.asyncio
async def test_confirm_reservations_fail_reservation_exam_date_is_before_today(
    mock_reservation_repository, reservation_service
):
    """
    [Reservation] 예약의 시작 시간이 현재 시간보다 이전이라면 에러를 반환한다(BadRequestError)
    """
    # given
    reservation_id = 1
    user_type = UserType.ADMIN

    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = {
        "id": reservation_id,
        "user_id": 1,
        "exam_date": datetime.now() - timedelta(days=1),
        "exam_start_time": time(14, 0),
        "exam_end_time": time(15, 0),
        "applicants": 30000,
        "status": ReservationStatus.PENDING.value,
    }

    # when
    with pytest.raises(BadRequestError) as e:
        await reservation_service.confirm_reservations(reservation_id=reservation_id, user_type=user_type)

    # then
    assert isinstance(e.value, BadRequestError)


@pytest.mark.asyncio
async def test_confirm_reservations_fail_slot_not_found(mock_reservation_repository, reservation_service):
    """
    [Reservation] 예약 가능한 슬롯이 없으면 에러를 반환한다(NotFoundError)
    """
    # given
    reservation_id = 1
    user_type = UserType.ADMIN

    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = {
        "id": reservation_id,
        "user_id": 1,
        "exam_date": datetime.now() + timedelta(days=5),
        "exam_start_time": time(14, 0),
        "exam_end_time": time(15, 0),
        "applicants": 30000,
        "status": ReservationStatus.PENDING.value,
    }
    mock_reservation_repository.get_overlapping_slots_with_external_session.return_value = []

    # when
    with pytest.raises(NotFoundError) as e:
        await reservation_service.confirm_reservations(reservation_id=reservation_id, user_type=user_type)

    # then
    assert isinstance(e.value, NotFoundError)


@pytest.mark.asyncio
async def test_confirm_reservations_fail_slot_remaining_applicants_not_enough(
    mock_reservation_repository, reservation_service
):
    """
    [Reservation] 예약 가능한 슬롯중 하나라도 남은인원(remaining_applicants)이 예약하려는 인원수보다 적으면 에러를 반환한다(BadRequestError)
    """
    # given
    reservation_id = 1
    user_type = UserType.ADMIN

    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = {
        "id": reservation_id,
        "user_id": 1,
        "exam_date": datetime.now() + timedelta(days=5),
        "exam_start_time": time(14, 0),
        "exam_end_time": time(15, 0),
        "applicants": 30000,
        "status": ReservationStatus.PENDING.value,
    }
    mock_reservation_repository.get_overlapping_slots_with_external_session.return_value = [
        {
            "id": 1,
            "exam_date": datetime.now(),
            "exam_start_time": time(14, 0),
            "exam_end_time": time(14, 30),
            "remaining_applicants": 40000,
        },
        {
            "id": 2,
            "exam_date": datetime.now(),
            "exam_start_time": time(14, 30),
            "exam_end_time": time(15, 0),
            "remaining_applicants": 1000,
        },
    ]

    # when
    with pytest.raises(BadRequestError) as e:
        await reservation_service.confirm_reservations(reservation_id=reservation_id, user_type=user_type)

    # then
    assert isinstance(e.value, BadRequestError)
