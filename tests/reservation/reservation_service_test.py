from datetime import date, time, timedelta

import pytest

from app.common.constants import ReservationStatus
from app.common.database.models.reservation import Reservation
from app.schemas.reservation_schema import ReservationCreateRequest


@pytest.mark.asyncio
async def test_create_reservation_success(mock_reservation_repository, reservation_service):
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
    mock_reservation_repository.get_reservations_by_exam_date.return_value = []
    mock_reservation_repository.create_reservation.return_value = Reservation(
        id=1,
        user_id=1,
        exam_date=exam_date,
        exam_start_date=start_time,
        exam_end_date=end_time,
        applicants=applicants,
        status=ReservationStatus.PENDING,
    )
    # when
    reservation = await reservation_service.create_reservation(input_data)
    # then
    mock_reservation_repository.get_reservations_by_exam_date.assert_called_once()
    mock_reservation_repository.create_reservation.assert_called_once_with(input_data)
    assert reservation.id == 1
    assert reservation.user_id == 1
    assert reservation.exam_date == exam_date
    assert reservation.exam_start_date == start_time
    assert reservation.exam_end_date == end_time
    assert reservation.applicants == applicants
    assert reservation.status == ReservationStatus.PENDING


# def test_create_reservation_fail_invalid_applicants_number(mock_reservation_repository, settings):
#     """
#     [Reservation] 응시 인원이 1 미만이거나 5만 명을 초과하면 예약 생성에 실패한다.
#     """
#     # given
#     pass


# def test_create_reservation_fail_past_exam_date(mock_reservation_repository, settings):
#     """
#     [Reservation] 시험 시작일이 과거인 경우 예약 생성에 실패한다.
#     """
#     # given
#     pass


# def test_create_reservation_fail_by_before_3_days(mock_reservation_repository, settings):
#     """
#     [Reservation] 시험시작일(YYYYMMDD)은 예약신청일 기준 최소 3일 전이어야 한다.
#     """
#     # given
#     pass


# def test_create_reservation_fail_when_overlapping_exceeds_limit(mock_reservation_repository, settings):
#     """
#     [Reservation] 겹치는 시간대의 확정된 예약 인원 합이 5만 명을 초과하면 예약 생성에 실패한다.
#     """
#     # given


# def test_create_reservation_success_when_overlapping_within_limit(mock_reservation_repository, settings):
#     """
#     [Reservation] 겹치는 시간대의 확정된 예약 인원 합이 5만 명 이하이면 예약 생성에 성공한다.
#     """


# def test_create_reservation_success_unconfirmed_not_counted_in_limit(mock_reservation_repository, settings):
#     """
#     [Reservation] 확정되지 않은 예약은 5만 명 제한에 포함되지 않는다.
#     """
#     # given
#     pass
