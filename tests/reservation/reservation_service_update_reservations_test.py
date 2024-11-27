from datetime import date, datetime, time, timedelta

import pytest

from app.common.constants import ReservationStatus, UserType
from app.common.exceptions import AuthorizationError, BadRequestError, NotFoundError
from app.schemas.reservation_schema import ReservationUpdateRequest


@pytest.mark.asyncio
async def test_update_reservations_success_by_admin(
    mock_reservation_repository,
    reservation_service,
    mock_slot_repository,
    mock_reservation,
    mock_slot,
    mock_user,
):
    """
    [Reservation] 관리자는 모든 확정되지 않은 예약을 업데이트할 수 있다
    """
    # given
    input_data = ReservationUpdateRequest(
        exam_date=date.today() + timedelta(days=5),
        exam_start_time=time(hour=9, minute=0),
        exam_end_time=time(hour=10, minute=0),
        applicants=1000,
    )

    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = mock_reservation(
        reservation_id=1,
        user_id=mock_user.id,
        exam_date=datetime.now() + timedelta(days=10),
        start_time=time(14, 0),
        end_time=time(15, 0),
        applicants=30000,
        status=ReservationStatus.PENDING,
    )
    mock_slot_repository.get_overlapping_slots_with_external_session.return_value = [
        mock_slot(
            slot_id=1,
            exam_date=input_data.exam_date,
            start_time=datetime.combine(input_data.exam_date, input_data.exam_start_time),
            end_time=datetime.combine(input_data.exam_date, input_data.exam_start_time) + timedelta(minutes=30),
            remaining_capacity=40000,
        ),
        mock_slot(
            slot_id=2,
            exam_date=input_data.exam_date,
            start_time=datetime.combine(input_data.exam_date, input_data.exam_start_time) + timedelta(minutes=30),
            end_time=datetime.combine(input_data.exam_date, input_data.exam_start_time) + timedelta(minutes=60),
            remaining_capacity=40000,
        ),
    ]
    mock_reservation_repository.update_reservation_with_external_session.return_value = None
    # when
    result = await reservation_service.update_reservation(
        input_data, reservation_id=1, user_id=1, user_type=UserType.ADMIN.value
    )
    # then
    mock_reservation_repository.update_reservation_with_external_session.assert_called_once()
    assert result.is_success


@pytest.mark.asyncio
async def test_update_reservations_fail_by_user(
    reservation_service,
    mock_reservation_repository,
    mock_reservation,
    mock_user,
):
    """
    [Reservation] 일반 유저는 다른 유저의 예약을 업데이트할 수 없다(AuthorizationError)
    """
    # given
    input_data = ReservationUpdateRequest(
        exam_date=date.today() + timedelta(days=5),
        exam_start_time=time(hour=9, minute=0),
        exam_end_time=time(hour=10, minute=0),
        applicants=1000,
    )
    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = mock_reservation(
        reservation_id=1,
        user_id=mock_user.id,
        exam_date=datetime.now() + timedelta(days=10),
        start_time=time(14, 0),
        end_time=time(15, 0),
        applicants=30000,
        status=ReservationStatus.PENDING,
    )
    # when
    with pytest.raises(AuthorizationError) as e:
        await reservation_service.update_reservation(input_data, reservation_id=1, user_id=2, user_type=UserType.USER)
    # then
    assert isinstance(e.value, AuthorizationError)
    mock_reservation_repository.update_reservation.assert_not_called()


@pytest.mark.asyncio
async def test_update_reservations_fail_reservation_not_found(
    reservation_service,
    mock_reservation_repository,
):
    """
    [Reservation] 존재하지 않는 예약을 업데이트할 수 없다(NotFoundError)
    """

    input_data = ReservationUpdateRequest(
        exam_date=date.today() + timedelta(days=5),
        exam_start_time=time(hour=9, minute=0),
        exam_end_time=time(hour=10, minute=0),
        applicants=1000,
    )
    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = None
    # when
    with pytest.raises(NotFoundError) as e:
        await reservation_service.update_reservation(input_data, reservation_id=1, user_id=1, user_type=UserType.USER)
    # then
    assert isinstance(e.value, NotFoundError)
    mock_reservation_repository.update_reservation.assert_not_called()


@pytest.mark.asyncio
async def test_update_reservations_fail_reservation_confirmed(
    reservation_service,
    mock_reservation_repository,
    mock_reservation,
    mock_user,
):
    """
    [Reservation] 확정된 예약은 업데이트할 수 없다
    """

    input_data = ReservationUpdateRequest(
        exam_date=date.today() + timedelta(days=5),
        exam_start_time=time(hour=9, minute=0),
        exam_end_time=time(hour=10, minute=0),
        applicants=1000,
    )
    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = mock_reservation(
        reservation_id=1,
        user_id=mock_user.id,
        exam_date=datetime.now() + timedelta(days=10),
        start_time=time(14, 0),
        end_time=time(15, 0),
        applicants=30000,
        status=ReservationStatus.CONFIRMED,
    )
    # when
    with pytest.raises(BadRequestError) as e:
        await reservation_service.update_reservation(input_data, reservation_id=1, user_id=1, user_type=UserType.USER)
    # then
    assert isinstance(e.value, BadRequestError)
    mock_reservation_repository.update_reservation.assert_not_called()


@pytest.mark.asyncio
async def test_update_reservations_fail_reservation_date_and_time_validation(
    reservation_service,
    mock_reservation_repository,
    mock_slot_repository,
    mock_reservation,
    mock_slot,
    mock_user,
):
    """
    [Reservation] 변경 하려는 예약 날짜 및 시간이 예약 가능한 시간인지 검증한다(InvalidValueError)
    """
    # given
    input_data = ReservationUpdateRequest(
        exam_date=date.today() + timedelta(days=5),
        exam_start_time=time(hour=9, minute=0),
        exam_end_time=time(hour=10, minute=0),
        applicants=1000,
    )
    mock_reservation_repository.get_reservation_by_id.return_value = mock_reservation(
        reservation_id=1,
        user_id=mock_user.id,
        exam_date=datetime.now() + timedelta(days=10),
        start_time=time(14, 0),
        end_time=time(15, 0),
        applicants=30000,
        status=ReservationStatus.PENDING,
    )
    mock_slot_repository.get_overlapping_slots_with_external_session.return_value = [
        mock_slot(
            slot_id=1,
            exam_date=input_data.exam_date,
            start_time=datetime.combine(input_data.exam_date, input_data.exam_start_time),
            end_time=datetime.combine(input_data.exam_date, input_data.exam_start_time) + timedelta(minutes=30),
            remaining_capacity=20000,
        ),
        mock_slot(
            slot_id=2,
            exam_date=input_data.exam_date,
            start_time=datetime.combine(input_data.exam_date, input_data.exam_start_time) + timedelta(minutes=30),
            end_time=datetime.combine(input_data.exam_date, input_data.exam_start_time) + timedelta(minutes=60),
            remaining_capacity=40000,
        ),
    ]
    # when
    with pytest.raises(BadRequestError) as e:
        await reservation_service.update_reservation(input_data, reservation_id=1, user_id=1, user_type=UserType.USER)
    # then
    assert isinstance(e.value, BadRequestError)
