from datetime import date, datetime, time, timedelta
from unittest.mock import Mock

import pytest

from app.common.constants import ReservationStatus
from app.schemas.reservation_schema import ReservationCreateRequest


@pytest.mark.asyncio
async def test_create_reservation_success(mock_reservation_repository, reservation_service, mock_session_factory):
    """
    [Reservation] 시험 날짜와 시간 정보를 올바르게 입력하면 예약을 생성할 수 있다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    applicants = 1000

    input_data = ReservationCreateRequest(
        user_id=1, exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )
    start_datetime = datetime.combine(exam_date, start_time)
    end_datetime = datetime.combine(exam_date, end_time)
    mock_reservation_repository.get_overlapping_reservations_with_external_session.return_value = []

    mock_reservation_repository.create_reservation_with_external_session.return_value = Mock(
        id=1,
        user_id=1,
        exam_date=exam_date,
        exam_start_date=start_datetime,
        exam_end_date=end_datetime,
        applicants=applicants,
        status=ReservationStatus.PENDING,
    )

    # when
    reservation = await reservation_service.create_reservation(input_data)

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
    mock_reservation_repository, reservation_service, applicants
):
    """
    [Reservation] 응시 인원이 1 미만이거나 5만 명을 초과하면 예약 생성에 실패한다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    input_data = ReservationCreateRequest(
        user_id=1, exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data)

    # then
    mock_reservation_repository.get_overlapping_reservations.assert_not_called()
    mock_reservation_repository.create_reservation.assert_not_called()
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_fail_past_exam_date(mock_reservation_repository, reservation_service):
    """
    [Reservation] 시험 시작일이 과거인 경우 예약 생성에 실패한다.
    """
    # given
    exam_date = date.today() - timedelta(days=1)  # 과거 날짜
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    input_data = ReservationCreateRequest(
        user_id=1, exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=1
    )

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data)

    # then
    mock_reservation_repository.get_overlapping_reservations_with_external_session.assert_not_called()
    mock_reservation_repository.create_reservation_with_external_session.assert_not_called()
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_fail_by_before_3_days(mock_reservation_repository, reservation_service):
    """
    [Reservation] 시험시작일은 예약신청일 기준 최소 3일 전이어야 한다.
    """
    # given
    exam_date = date.today() + timedelta(days=2)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    input_data = ReservationCreateRequest(
        user_id=1, exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=1
    )

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data)

    # then
    mock_reservation_repository.get_overlapping_reservations_with_external_session.assert_not_called()
    mock_reservation_repository.create_reservation_with_external_session.assert_not_called()
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_fail_when_overlapping_exceeds_limit(mock_reservation_repository, reservation_service):
    """
    [Reservation] 겹치는 시간대의 확정된 예약 인원 합이 5만 명을 초과하면 예약 생성에 실패한다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    applicants = 2
    input_data = ReservationCreateRequest(
        user_id=1, exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )

    mock_reservation_repository.get_overlapping_reservations.return_value = [
        Mock(
            exam_start_date=datetime.combine(exam_date, start_time),
            exam_end_date=datetime.combine(exam_date, end_time),
            applicants=49999,
        )
    ]

    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.create_reservation(input_data)

    # then
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_create_reservation_success_when_overlapping_within_limit(
    mock_reservation_repository, reservation_service
):
    """
    [Reservation] 겹치는 시간대의 확정된 예약 인원 합이 5만 명 이하이면 예약 생성에 성공한다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    start_time = time(hour=9, minute=0)
    end_time = time(hour=11, minute=0)
    applicants = 2
    input_data = ReservationCreateRequest(
        user_id=1, exam_date=exam_date, exam_start_time=start_time, exam_end_time=end_time, applicants=applicants
    )
    start_datetime = datetime.combine(exam_date, start_time)
    end_datetime = datetime.combine(exam_date, end_time)

    mock_reservation_repository.get_overlapping_reservations_with_external_session.return_value = [
        Mock(
            exam_start_date=datetime.combine(exam_date, start_time),
            exam_end_date=datetime.combine(exam_date, end_time),
            applicants=49998,
        )
    ]
    mock_reservation_repository.create_reservation_with_external_session.return_value = Mock(
        id=1,
        user_id=1,
        exam_date=exam_date,
        exam_start_date=start_datetime,
        exam_end_date=end_datetime,
        applicants=applicants,
        status=ReservationStatus.PENDING,
    )

    # when
    reservation = await reservation_service.create_reservation(input_data)

    # then
    assert reservation.id == 1
    assert reservation.user_id == 1
    assert reservation.exam_date == exam_date
    assert reservation.exam_start_time == start_time
    assert reservation.exam_end_time == end_time
    assert reservation.applicants == applicants
    assert reservation.status == ReservationStatus.PENDING
