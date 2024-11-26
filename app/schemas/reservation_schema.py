from datetime import date, time
from typing import Optional

from pydantic import BaseModel

from app.common.constants import ReservationStatus


class ReservationCreateRequest(BaseModel):
    user_id: Optional[int] = None
    exam_date: date
    exam_start_time: time
    exam_end_time: time
    applicants: int


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    exam_date: date
    exam_start_time: time
    exam_end_time: time
    applicants: int
    status: ReservationStatus


class AvailableSlot(BaseModel):
    id: int
    date: date
    start_time: time
    end_time: time
    remaining_capacity: int

    model_config = {"from_attributes": True}


class AvailableReservationResponse(BaseModel):
    available_slots: list[AvailableSlot]
