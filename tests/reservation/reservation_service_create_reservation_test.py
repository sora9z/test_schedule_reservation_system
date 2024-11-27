from datetime import date, datetime, time, timedelta

import pytest

from app.common.constants import ReservationStatus
from app.schemas.reservation_schema import ReservationCreateRequest


@pytest.mark.asyncio
async def test_create_reservation_success(
    mock_reservation_repository,
    mock_slot_repository,
    reservation_service,
    mock_reservation,
    mock_slot,
    mock_user,
):
    """
    [Reservation] 시험 날짜와 시간 정보를 올바르게 입력하면 예약을 생성할 수 있다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=10, minute=0)
    applicants = 1000

    input_data = ReservationCreateRequest(
        exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )
    mock_slot_repository.get_overlapping_slots_with_external_session.return_value = [
        mock_slot(
            slot_id=1,
            exam_date=exam_date,
            start_time=datetime.combine(exam_date, start_time),
            end_time=datetime.combine(exam_date, start_time) + timedelta(minutes=30),
            remaining_capacity=40000,
        ),
        mock_slot(
            slot_id=2,
            exam_date=exam_date,
            start_time=datetime.combine(exam_date, start_time) + timedelta(minutes=30),
            end_time=datetime.combine(exam_date, start_time) + timedelta(minutes=60),
            remaining_capacity=40000,
        ),
    ]
    mock_reservation_repository.create_reservation_with_external_session.return_value = mock_reservation(
        reservation_id=1,
        user_id=mock_user.id,
        exam_date=exam_date,
        start_time=start_time,
        end_time=end_time,
        applicants=applicants,
        status=ReservationStatus.PENDING,
    )

    # when
    reservation = await reservation_service.create_reservation(input_data, user_id=1)

    # then
    assert reservation.id == 1
    assert reservation.user_id == 1
    assert reservation.exam_date == exam_date
    assert reservation.exam_start_time == start_time
    assert reservation.exam_end_time == end_time
    assert reservation.applicants == applicants
    assert reservation.status == ReservationStatus.PENDING


@pytest.mark.asyncio
@pytest.mark.parametrize("applicants", [-1, 50001])
async def test_create_reservation_fail_invalid_applicants_number(
    mock_reservation_repository,
    mock_slot_repository,
    reservation_service,
    applicants,
):
    """
    [Reservation] 응시 인원이 1 미만이거나 5만 명을 초과하면 예약 생성에 실패한다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    input_data = ReservationCreateRequest(
        exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data, user_id=1)

    # then
    mock_slot_repository.get_overlapping_slots_with_external_session.assert_not_called()
    mock_reservation_repository.create_reservation_with_external_session.assert_not_called()
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_fail_past_exam_date(
    mock_reservation_repository,
    mock_slot_repository,
    reservation_service,
):
    """
    [Reservation] 시험 시작일이 과거인 경우 예약 생성에 실패한다.
    """
    # given
    exam_date = date.today() - timedelta(days=1)  # 과거 날짜
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    input_data = ReservationCreateRequest(
        exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=1
    )

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data, user_id=1)

    # then
    mock_slot_repository.get_overlapping_slots_with_external_session.assert_not_called()
    mock_reservation_repository.create_reservation_with_external_session.assert_not_called()
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_fail_by_before_3_days(
    mock_reservation_repository,
    mock_slot_repository,
    reservation_service,
):
    """
    [Reservation] 시험시작일은 예약신청일 기준 최소 3일 전이어야 한다.
    """
    # given
    exam_date = date.today() + timedelta(days=2)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    input_data = ReservationCreateRequest(
        exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=1
    )

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data, user_id=1)

    # then
    mock_slot_repository.get_overlapping_slots_with_external_session.assert_not_called()
    mock_reservation_repository.create_reservation_with_external_session.assert_not_called()
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_fail_when_overlapping_exceeds_limit(
    mock_slot_repository,
    reservation_service,
    mock_slot,
):
    """
    [Reservation] 겹치는 시간대의 슬롯 중 예약 인원을 수용하지 않는 슬롯이 있으면 예약 생성에 실패한다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    applicants = 20000
    input_data = ReservationCreateRequest(
        exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )

    mock_slot_repository.get_overlapping_slots_with_external_session.return_value = [
        mock_slot(
            slot_id=1,
            exam_date=exam_date,
            start_time=datetime.combine(exam_date, start_time),
            end_time=datetime.combine(exam_date, start_time) + timedelta(minutes=30),
            remaining_capacity=20000,
        ),
        mock_slot(
            slot_id=2,
            exam_date=exam_date,
            start_time=datetime.combine(exam_date, start_time) + timedelta(minutes=30),
            end_time=datetime.combine(exam_date, start_time) + timedelta(minutes=60),
            remaining_capacity=40000,
        ),
    ]

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data, user_id=1)

    # then
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_success_when_overlapping_within_limit(
    mock_reservation_repository,
    mock_slot_repository,
    reservation_service,
    mock_slot,
    mock_reservation,
    mock_user,
):
    """
    [Reservation] 겹치는 시간대의 슬롯이 모두 예약 인원을 수용할 수 있으면 예약 생성에 성공한다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    applicants = 20000
    input_data = ReservationCreateRequest(
        exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )

    mock_slot_repository.get_overlapping_slots_with_external_session.return_value = [
        mock_slot(
            slot_id=1,
            exam_date=exam_date,
            start_time=datetime.combine(exam_date, start_time),
            end_time=datetime.combine(exam_date, start_time) + timedelta(minutes=30),
            remaining_capacity=30000,
        ),
        mock_slot(
            slot_id=2,
            exam_date=exam_date,
            start_time=datetime.combine(exam_date, start_time) + timedelta(minutes=30),
            end_time=datetime.combine(exam_date, start_time) + timedelta(minutes=60),
            remaining_capacity=20000,
        ),
    ]
    mock_reservation_repository.create_reservation_with_external_session.return_value = mock_reservation(
        reservation_id=1,
        user_id=mock_user.id,
        exam_date=exam_date,
        start_time=start_time,
        end_time=end_time,
        applicants=applicants,
        status=ReservationStatus.PENDING,
    )

    # when
    reservation = await reservation_service.create_reservation(input_data, user_id=1)

    # then
    assert reservation.id == 1
    assert reservation.user_id == 1
    assert reservation.exam_date == exam_date
    assert reservation.exam_start_time == start_time
    assert reservation.exam_end_time == end_time
    assert reservation.applicants == applicants
    assert reservation.status == ReservationStatus.PENDING
