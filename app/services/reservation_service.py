import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.ext.asyncio import async_scoped_session

from app.common.constants import ReservationStatus, UserType
from app.common.database.models.slot import Slot
from app.common.exceptions import AuthorizationError, BadRequestError, NotFoundError
from app.common.respository.reservation_repository import ReservationRepository
from app.common.respository.slot_repository import SlotRepository
from app.config import Config
from app.schemas.reservation_schema import (
    AvailableReservationResponse,
    AvailableSlot,
    ConfirmReservationResponse,
    ReservationCreateRequest,
    ReservationListResponse,
    ReservationResponse,
)

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(
        self,
        repository: ReservationRepository,
        slot_repository: SlotRepository,
        settings: Config,
        session_factory: async_scoped_session,
    ) -> None:
        self.repository = repository
        self.slot_repository = slot_repository
        self.settings = settings
        self.session_factory = session_factory

    async def create_reservation(self, input_data: ReservationCreateRequest) -> ReservationResponse:
        def _validate_reservation(exam_date, exam_start_time, exam_end_time, applicants):
            today = datetime.now().date()
            if exam_date < today:
                raise ValueError("시험 날짜는 오늘 이후로 설정해야 합니다.")
            if exam_date < today + timedelta(days=3):
                raise ValueError("시험 날짜는 예약 신청일 기준 최소 3일 전이어야 합니다.")
            if exam_start_time >= exam_end_time:
                raise ValueError("시험 시작 시간은 시험 종료 시간보다 이전이어야 합니다.")
            if applicants < 1 or applicants > self.settings.MAX_APPLICANTS:
                raise ValueError(f"응시자 수는 1 이상 {self.settings.MAX_APPLICANTS} 이하로 설정해야 합니다.")

        async with self.session_factory() as session:
            async with session.begin():
                try:
                    _validate_reservation(
                        input_data.exam_date,
                        input_data.exam_start_time,
                        input_data.exam_end_time,
                        input_data.applicants,
                    )

                    input_data.user_id = 1  # TODO: 임시 유저 아이디 설정

                    # 시험 시작 일시와 종료 일시 생성
                    exam_start_datetime = datetime.combine(input_data.exam_date, input_data.exam_start_time)
                    exam_end_datetime = datetime.combine(input_data.exam_date, input_data.exam_end_time)

                    # 겹치는 슬롯의 총 응시자 수 계산
                    overlapping_slots = await self.slot_repository.get_overlapping_slots_with_external_session(
                        exam_start_datetime, exam_end_datetime, "[]", session
                    )
                    total_applicants = sum(
                        overlapping_slot.remaining_capacity for overlapping_slot in overlapping_slots
                    )

                    # 총 응시자 수가 지원자 수보다 많으면 예약 생성 불가
                    if total_applicants + input_data.applicants > self.settings.MAX_APPLICANTS:
                        raise ValueError("총 응시자 수가 지원자 수보다 많습니다.")

                    reservation_data = {
                        "user_id": input_data.user_id,
                        "exam_date": input_data.exam_date,
                        "exam_start_time": input_data.exam_start_time,
                        "exam_end_time": input_data.exam_end_time,
                        "applicants": input_data.applicants,
                        "status": ReservationStatus.PENDING,
                    }
                    result = await self.repository.create_reservation_with_external_session(reservation_data, session)

                    return ReservationResponse(
                        id=result.id,
                        user_id=result.user_id,
                        exam_date=result.exam_date,
                        exam_start_time=result.exam_start_time,
                        exam_end_time=result.exam_end_time,
                        applicants=result.applicants,
                        status=result.status,
                    )
                except Exception as e:
                    logger.error(f"[service/reservation_service] create_reservation error: {e}")
                    raise e

    async def get_available_reservation(self, exam_date: datetime.date) -> AvailableReservationResponse:
        try:
            # 입력값 검증
            if exam_date < datetime.now().date() + timedelta(days=3):
                raise BadRequestError("예약 가능일은 시험일 3일 전부터 조회할 수 있습니다.")

            # 예약 가능한 시간대 조회
            available_slots = await self.slot_repository.get_available_slots(exam_date)

            return AvailableReservationResponse(
                available_slots=[AvailableSlot.model_validate(slot) for slot in available_slots] or []
            )
        except Exception as e:
            logger.error(f"[service/reservation_service] get_available_reservation error: {e}")
            raise e

    async def get_reservations_by_user(self, user_id: int) -> ReservationListResponse:
        try:
            reservations = await self.repository.get_reservations_by_user_id(user_id)
            return ReservationListResponse(
                reservations=[ReservationResponse.model_validate(reservation) for reservation in reservations] or []
            )
        except Exception as e:
            logger.error(f"[service/reservation_service] get_reservations_by_user error: {e}")
            raise e

    async def get_reservations_by_admin(self, user_type: UserType) -> ReservationListResponse:
        try:
            if user_type != UserType.ADMIN.value:
                raise AuthorizationError("권한이 없습니다.")
            reservations = await self.repository.get_reservations()
            return ReservationListResponse(
                reservations=[ReservationResponse.model_validate(reservation) for reservation in reservations] or []
            )
        except Exception as e:
            logger.error(f"[service/reservation_service] get_reservations_by_admin error: {e}")
            raise e

    async def confirm_reservations(self, reservation_id: int, user_type: UserType) -> ConfirmReservationResponse:
        try:
            if user_type != UserType.ADMIN.value:
                raise AuthorizationError("권한이 없습니다.")

            async with self.session_factory() as session:
                async with session.begin():
                    reservation = await self._fetch_and_validate_reservation(session, reservation_id)
                    overlapping_slots = await self._fetch_and_validate_slots(session, reservation)
                    await self._update_slots_and_confirm_reservation(session, reservation, overlapping_slots)
                    await session.commit()
                return ConfirmReservationResponse(is_success=True)

        except Exception as e:
            logger.error(f"[service/reservation_service] confirm_reservations error: {e}")
            raise e

    async def _update_slots_and_confirm_reservation(self, session, reservation, overlapping_slots):
        for slot in overlapping_slots:
            slot.remaining_capacity -= reservation.applicants

        reservation.status = ReservationStatus.CONFIRMED
        reservation.slots = overlapping_slots
        await self.repository.update_reservation_with_external_session(reservation, session)

    async def _fetch_and_validate_slots(self, session, reservation):
        exam_start_datetime = datetime.combine(reservation.exam_date, reservation.exam_start_time)
        exam_end_datetime = datetime.combine(reservation.exam_date, reservation.exam_end_time)

        overlapping_slots = await self.slot_repository.get_overlapping_slots_with_external_session(
            exam_start_datetime, exam_end_datetime, "[]", session
        )
        if not overlapping_slots or len(overlapping_slots) == 0:
            raise NotFoundError("슬롯을 찾을 수 없습니다.")

            # 각 슬롯의 남은 인원수가 하나라도 예약하려는 인원수보다 적으면 안된다.
        if not self._check_remaining_capacity(overlapping_slots, reservation.applicants):
            raise BadRequestError("예약 불가능한 시간대입니다.")
        return overlapping_slots

    async def _fetch_and_validate_reservation(self, session, reservation_id):
        reservation = await self.repository.get_reservation_by_id_with_external_session(reservation_id, session)
        if not reservation:
            raise NotFoundError("예약을 찾을 수 없습니다.")

        if (reservation.status != ReservationStatus.PENDING) or (
            datetime.combine(reservation.exam_date, reservation.exam_start_time) < datetime.now()
        ):
            raise BadRequestError("확정 가능한 예약이 아닙니다.")
        return reservation

    def _check_remaining_capacity(self, overlapping_slots: List[Slot], reservation_applicants: int) -> None:
        for slot in overlapping_slots:
            if slot.remaining_capacity < reservation_applicants:
                return False
        return True
