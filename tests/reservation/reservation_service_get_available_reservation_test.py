from datetime import date, time, timedelta

import pytest


@pytest.mark.asyncio
async def test_get_available_reservation_success(mock_slot_repository, reservation_service):
    """
    [Reservation] 예약일을 입력하면 예약 가능한 시간대와 수용 가능한 인원을 조회할 수 있다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)

    mock_slot_repository.get_available_slots.return_value = [
        {
            "id": 1,
            "date": exam_date,
            "start_time": time(hour=9, minute=0),
            "end_time": time(hour=10, minute=0),
            "remaining_capacity": 50000,
        },
        {
            "id": 2,
            "date": exam_date,
            "start_time": time(hour=10, minute=0),
            "end_time": time(hour=11, minute=0),
            "remaining_capacity": 3000,
        },
    ]
    # when
    result = await reservation_service.get_available_reservation(exam_date)
    # then
    mock_slot_repository.get_available_slots.assert_called_once_with(exam_date)
    assert len(result.available_slots) == 2
    assert result.available_slots[0].id == 1
    assert result.available_slots[0].start_time == time(hour=9, minute=0)
    assert result.available_slots[0].end_time == time(hour=10, minute=0)
    assert result.available_slots[0].remaining_capacity == 50000
    assert result.available_slots[1].id == 2
    assert result.available_slots[1].start_time == time(hour=10, minute=0)
    assert result.available_slots[1].end_time == time(hour=11, minute=0)
    assert result.available_slots[1].remaining_capacity == 3000


@pytest.mark.asyncio
async def test_get_available_reservation_fail_by_before_3_days(reservation_service):
    """
    [Reservation] 조회일이 3일 이전이면 ValueError 예외가 발생한다.
    """
    # given
    exam_date = date.today() - timedelta(days=3)
    # when
    with pytest.raises(ValueError) as e:
        await reservation_service.get_available_reservation(exam_date)
    # then
    assert isinstance(e.value, ValueError)


@pytest.mark.asyncio
async def test_get_available_reservation_fail_by_no_available_slot(mock_slot_repository, reservation_service):
    """
    [Reservation] 예약 가능한 시간대가 없으면 빈 배열을 반환한다.
    """
    # given
    exam_date = date.today() + timedelta(days=5)
    mock_slot_repository.get_available_slots.return_value = []
    # when
    result = await reservation_service.get_available_reservation(exam_date)
    # then
    assert len(result.available_slots) == 0
