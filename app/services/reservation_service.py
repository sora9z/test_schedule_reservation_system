import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import async_scoped_session

from app.common.constants import ReservationStatus, UserType
from app.common.database.models.reservation import Reservation
from app.common.exceptions import AuthorizationError, BadRequestError, NotFoundError
from app.common.respository.reservation_repository import ReservationRepository
from app.common.respository.slot_repository import SlotRepository
from app.config import Config
from app.schemas.reservation_schema import (
    AvailableReservationResponse,
    AvailableSlot,
    ConfirmReservationResponse,
    DeleteReservationResponse,
    ReservationCreateRequest,
    ReservationListResponse,
    ReservationResponse,
    ReservationUpdateRequest,
    ReservationUpdateResponse,
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

    async def create_reservation(self, input_data: ReservationCreateRequest, user_id: int) -> ReservationResponse:
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    await self._validate_reservation_input(
                        input_data.exam_date,
                        input_data.exam_start_time,
                        input_data.exam_end_time,
                        input_data.applicants,
                        session,
                    )
                    await self._fetch_and_validate_slots(
                        input_data.exam_date,
                        input_data.exam_start_time,
                        input_data.exam_end_time,
                        input_data.applicants,
                        session,
                    )

                    reservation_data = Reservation(
                        user_id=user_id,
                        exam_date=input_data.exam_date,
                        exam_start_time=input_data.exam_start_time,
                        exam_end_time=input_data.exam_end_time,
                        applicants=input_data.applicants,
                        status=ReservationStatus.PENDING,
                    )
                    result = await self.repository.create_reservation_with_external_session(reservation_data, session)

                    return ReservationResponse.model_validate(result)
        except Exception as e:
            logger.error(f"[service/reservation_service] create_reservation error: {e}")
            raise e

    async def confirm_reservations(self, reservation_id: int, user_type: UserType) -> ConfirmReservationResponse:
        try:
            if user_type != UserType.ADMIN.value:
                raise AuthorizationError("권한이 없습니다.")

            async with self.session_factory() as session:
                async with session.begin():
                    reservation = await self._fetch_and_validate_reservation(session, reservation_id)
                    overlapping_slots = await self._fetch_and_validate_slots(
                        reservation.exam_date,
                        reservation.exam_start_time,
                        reservation.exam_end_time,
                        reservation.applicants,
                        session,
                    )
                    await self._update_slots_and_confirm_reservation(session, reservation, overlapping_slots)
                    await session.commit()
                return ConfirmReservationResponse(is_success=True)

        except Exception as e:
            logger.error(f"[service/reservation_service] confirm_reservations error: {e}")
            raise e

    async def update_reservation(
        self, input_data: ReservationUpdateRequest, reservation_id: int, user_id: int, user_type: UserType
    ) -> ReservationUpdateResponse:

        try:
            async with self.session_factory() as session:
                async with session.begin():
                    reservation = await self._fetch_and_validate_reservation(session, reservation_id)

                    if user_type != UserType.ADMIN.value:
                        if reservation.user_id != user_id:
                            raise AuthorizationError("권한이 없습니다.")

                    await self._validate_reservation_input(
                        input_data.exam_date or reservation.exam_date,
                        input_data.exam_start_time or reservation.exam_start_time,
                        input_data.exam_end_time or reservation.exam_end_time,
                        input_data.applicants or None,
                        session,
                    )

                    if input_data.exam_date or input_data.exam_start_time or input_data.exam_end_time:
                        await self._fetch_and_validate_slots(
                            input_data.exam_date or reservation.exam_date,
                            input_data.exam_start_time or reservation.exam_start_time,
                            input_data.exam_end_time or reservation.exam_end_time,
                            input_data.applicants or reservation.applicants,
                            session,
                        )

                    reservation.exam_date = input_data.exam_date or reservation.exam_date
                    reservation.exam_start_time = input_data.exam_start_time or reservation.exam_start_time
                    reservation.exam_end_time = input_data.exam_end_time or reservation.exam_end_time
                    reservation.applicants = input_data.applicants or reservation.applicants

                    await self.repository.update_reservation_with_external_session(reservation, session)
                    await session.commit()
                return ReservationUpdateResponse(is_success=True)
        except Exception as e:
            logger.error(f"[service/reservation_service] update_reservation error: {e}")
            raise e

    async def delete_reservation(self, reservation_id: int, user_id: int, user_type: UserType):
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    reservation = await self.repository.get_reservation_by_id_with_external_session(
                        reservation_id, session
                    )
                    if not reservation:
                        raise NotFoundError("예약을 찾을 수 없습니다.")
                    if user_type == UserType.USER.value and reservation.user_id != user_id:
                        raise AuthorizationError("권한이 없습니다.")

                    if reservation.status == ReservationStatus.CONFIRMED:
                        exam_start_datetime = datetime.combine(reservation.exam_date, reservation.exam_start_time)
                        exam_end_datetime = datetime.combine(reservation.exam_date, reservation.exam_end_time)
                        overlapping_slots = await self.slot_repository.get_overlapping_slots_with_external_session(
                            exam_start_datetime, exam_end_datetime, "[]", session
                        )
                        for slot in overlapping_slots:
                            slot.remaining_capacity += reservation.applicants
                            session.add(slot)
                    await self.repository.delete_reservation_with_external_session(reservation.id, session)
                    await session.commit()
                return DeleteReservationResponse(is_success=True)
        except Exception as e:
            logger.error(f"[service/reservation_service] delete_reservation error: {e}")
            raise e

    async def _update_slots_and_confirm_reservation(self, session, reservation, overlapping_slots):
        for slot in overlapping_slots:
            slot.remaining_capacity -= reservation.applicants

        reservation.status = ReservationStatus.CONFIRMED
        reservation.slots = overlapping_slots
        await self.repository.update_reservation_with_external_session(reservation, session)

    async def _fetch_and_validate_slots(self, exam_date, exam_start_time, exam_end_time, applicants, session):
        exam_start_datetime = datetime.combine(exam_date, exam_start_time)
        exam_end_datetime = datetime.combine(exam_date, exam_end_time)

        # 겹치는 슬롯중 최소 남은 인원수가 지원자 수보다 적으면 안된다
        overlapping_slots = await self.slot_repository.get_overlapping_slots_with_external_session(
            exam_start_datetime, exam_end_datetime, "[]", session
        )
        if overlapping_slots:
            min_remaining_capacity = min(overlapping_slot.remaining_capacity for overlapping_slot in overlapping_slots)
            if min_remaining_capacity < applicants:
                raise ValueError("예약 불가능한 시간대입니다.")
        else:
            raise ValueError("겹치는 슬롯이 없습니다.")
        return overlapping_slots

    async def _fetch_and_validate_reservation(self, session, reservation_id):
        reservation = await self.repository.get_reservation_by_id_with_external_session(reservation_id, session)
        if not reservation:
            raise NotFoundError("예약을 찾을 수 없습니다.")
        if (reservation.status != ReservationStatus.PENDING) or (
            datetime.combine(reservation.exam_date, reservation.exam_start_time) < datetime.now()
        ):
            raise BadRequestError("수정 가능한 예약이 아닙니다.")
        return reservation

    async def _validate_reservation_input(self, exam_date, exam_start_time, exam_end_time, applicants, session):
        """
        [예약 생성 및 업데이트 시 검증 로직]
        - 예약 날짜 및 시간 검증
        - 응시자 수 검증
        """

        today = datetime.now().date()
        if exam_date and (exam_date < today or exam_date < today + timedelta(days=3)):
            raise ValueError("시험 날짜는 예약 신청일 기준 최소 3일 전이어야 합니다.")
        if exam_start_time and exam_end_time and (exam_start_time >= exam_end_time):
            raise ValueError("시험 시작 시간은 시험 종료 시간보다 이전이어야 합니다.")
        if applicants and (applicants < 1 or applicants > self.settings.MAX_APPLICANTS):
            raise ValueError(f"응시자 수는 1 이상 {self.settings.MAX_APPLICANTS} 이하로 설정해야 합니다.")
