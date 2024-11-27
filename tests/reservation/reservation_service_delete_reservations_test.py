from datetime import datetime, time, timedelta

import pytest

from app.common.constants import ReservationStatus, UserType
from app.common.exceptions import AuthorizationError

# 예약을 조회한다
# 타입이 유저이면 예약한 유저와 같은지 확인한다. 다르면 애러
# 확정된 예약이면 관련 슬롯을 가져온다
# 슬롯을 업데이트한다
# 예약을 삭제한다


@pytest.mark.asyncio
async def test_delete_reservations_success_confirmed(
    reservation_service,
    mock_reservation_repository,
    mock_slot_repository,
    mock_reservation,
    mock_slot,
    mock_user,
):
    """
    [Reservation] 관리자는 확정된 예약을 삭제할 수 있다.
    """
    # given
    reservation_id = 1
    user_id = 1
    user_type = UserType.ADMIN

    exam_date = datetime.now() + timedelta(days=5)
    start_time = time(14, 0)
    end_time = time(15, 0)
    applicants = 30000
    status = ReservationStatus.CONFIRMED

    reservation = mock_reservation(
        reservation_id,
        user_id=mock_user.id,
        exam_date=exam_date,
        start_time=start_time,
        end_time=end_time,
        applicants=applicants,
        status=status,
    )

    slot1 = mock_slot(1, exam_date, start_time, time(14, 30), 30000)
    slot2 = mock_slot(2, exam_date, time(14, 30), end_time, 50000)
    mock_slot_repository.get_overlapping_slots_with_external_session.return_value = [slot1, slot2]
    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = reservation
    mock_slot_repository.update_slot_with_external_session.return_value = None
    mock_reservation_repository.delete_reservation_with_external_session.return_value = None
    # when
    result = await reservation_service.delete_reservation(reservation_id, user_id, user_type)
    # then
    assert result is None
    mock_slot_repository.update_slot_with_external_session.assert_called()
    mock_reservation_repository.delete_reservation_with_external_session.assert_called()


@pytest.mark.asyncio
async def test_delete_reservations_success_by_admin(
    mock_reservation_repository,
    reservation_service,
    mock_reservation,
    mock_user,
):
    """
    [Reservation] 일반 사용자는 자신의 예약을 삭제할 수 있다.
    """
    # given
    reservation_id = 1
    user_id = 1
    user_type = UserType.USER

    exam_date = datetime.now() + timedelta(days=5)
    start_time = time(14, 0)
    end_time = time(15, 0)
    applicants = 30000
    status = ReservationStatus.PENDING

    reservation = mock_reservation(
        reservation_id,
        user_id=mock_user.id,
        exam_date=exam_date,
        start_time=start_time,
        end_time=end_time,
        applicants=applicants,
        status=status,
    )
    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = reservation
    mock_reservation_repository.delete_reservation_with_external_session.return_value = None
    # when
    result = await reservation_service.delete_reservation(reservation_id, user_id, user_type)
    # then
    assert result is None
    mock_reservation_repository.delete_reservation_with_external_session.assert_called()


@pytest.mark.asyncio
async def test_delete_reservations_fail(
    mock_reservation_repository,
    reservation_service,
    mock_reservation,
    mock_user,
):
    """
    [Reservation] 일반 사용자는 다른 사용자의 예약을 삭제할 수 없다.
    """
    # given
    reservation_id = 1
    user_id = 1
    user_type = UserType.USER

    exam_date = datetime.now() + timedelta(days=5)
    start_time = time(14, 0)
    end_time = time(15, 0)
    applicants = 30000
    status = ReservationStatus.PENDING

    reservation = mock_reservation(
        reservation_id,
        user_id=mock_user.id,
        exam_date=exam_date,
        start_time=start_time,
        end_time=end_time,
        applicants=applicants,
        status=status,
    )
    mock_reservation_repository.get_reservation_by_id_with_external_session.return_value = reservation
    # when
    with pytest.raises(AuthorizationError) as e:
        await reservation_service.delete_reservation(reservation_id, user_id, user_type)
    # then
    assert isinstance(e.value, AuthorizationError)
