from datetime import date, time, timedelta
from unittest.mock import Mock

import pytest

from app.common.exceptions import BadRequestError


@pytest.mark.asyncio
async def test_get_available_reservation_success(mock_slot_repository, reservation_service):
    """
    [Reservation] 예약일을 입력하면 예약 가능한 시간대와 수용 가능한 인원을 조회할 수 있다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    mock_slot_repository.get_available_slots.return_value = [
        Mock(
            id=1,
            date=exam_date,
            start_time=time(hour=9, minute=0),
            end_time=time(hour=10, minute=0),
            remaining_capacity=50000,
        ),
        Mock(
            id=2,
            date=exam_date,
            start_time=time(hour=10, minute=0),
            end_time=time(hour=11, minute=0),
            remaining_capacity=3000,
        ),
    ]
    # when
    result = await reservation_service.get_available_reservation(exam_date)
    # then
    assert result == [
        {"slot_id": 1, "start_time": "09:00", "end_time": "10:00", "remaining_capacity": 50000},
        {"slot_id": 2, "start_time": "10:00", "end_time": "11:00", "remaining_capacity": 3000},
    ]
    mock_slot_repository.get_available_slots.assert_called_once_with(exam_date)


@pytest.mark.asyncio
async def test_get_available_reservation_fail_by_before_3_days(mock_slot_repository, reservation_service):
    """
    [Reservation] 조회일이 3일 이전이면 BadRequestException 예외가 발생한다.
    """
    # given
    exam_date = date.today() - timedelta(days=3)
    # when
    with pytest.raises(BadRequestError) as e:
        await reservation_service.get_available_reservation(exam_date)
    # then
    assert e.value.status_code == 400
    assert e.value.detail == "예약일은 시험일 3일 전부터 조회할 수 있습니다."
