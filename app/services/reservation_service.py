import logging
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.ext.asyncio import async_scoped_session

from app.common.constants import ReservationStatus
from app.common.respository.reservation_repository import ReservationRepository
from app.config import Config
from app.schemas.reservation_schema import ReservationCreateRequest, ReservationResponse

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(
        self, repository: ReservationRepository, settings: Config, session_factory: async_scoped_session
    ) -> None:
        self.repository = repository
        self.settings = settings
        self.session_factory = session_factory

    async def create_reservation(self, input_data: ReservationCreateRequest) -> ReservationResponse:
        async with self.session_factory() as session:
            async with session.begin():
                try:
                    self._validate_reservation(
                        input_data.exam_date,
                        input_data.exam_start_time,
                        input_data.exam_end_time,
                        input_data.applicants,
                    )

                    input_data.user_id = 1

                    # 시험 시작 일시와 종료 일시 생성
                    exam_start_datetime = datetime.combine(input_data.exam_date, input_data.exam_start_time)
                    exam_end_datetime = datetime.combine(input_data.exam_date, input_data.exam_end_time)

                    # 겹치는 예약의 총 응시자 수 계산
                    overlapping_reservations = await self.repository.get_overlapping_reservations_with_external_session(
                        exam_start_datetime, exam_end_datetime, "[]", session
                    )
                    total_applicants = sum(
                        overlapping_reservation.applicants for overlapping_reservation in overlapping_reservations
                    )

                    # 총 응시자 수가 지원자 수보다 많으면 예약 생성 불가
                    if total_applicants + input_data.applicants > self.settings.MAX_APPLICANTS:
                        raise ValueError("총 응시자 수가 지원자 수보다 많습니다.")

                    reservation_data = {
                        "user_id": input_data.user_id,
                        "exam_date": input_data.exam_date,
                        "exam_start_date": exam_start_datetime,
                        "exam_end_date": exam_end_datetime,
                        "applicants": input_data.applicants,
                        "status": ReservationStatus.PENDING,
                        "time_range": func.tstzrange(exam_start_datetime, exam_end_datetime, "[]"),
                    }
                    result = await self.repository.create_reservation_with_external_session(reservation_data, session)

                    return ReservationResponse(
                        id=result.id,
                        user_id=result.user_id,
                        exam_date=result.exam_date,
                        exam_start_time=result.exam_start_date.time(),
                        exam_end_time=result.exam_end_date.time(),
                        applicants=result.applicants,
                        status=result.status,
                    )
                except Exception as e:
                    logger.error(f"[service/reservation_service] create_reservation error: {e}")
                    raise e

    def _validate_reservation(self, exam_date, exam_start_time, exam_end_time, applicants):
        today = datetime.now().date()
        if exam_date < today:
            raise ValueError("시험 날짜는 오늘 이후로 설정해야 합니다.")
        if exam_date < today + timedelta(days=3):
            raise ValueError("시험 날짜는 예약 신청일 기준 최소 3일 전이어야 합니다.")
        if exam_start_time >= exam_end_time:
            raise ValueError("시험 시작 시간은 시험 종료 시간보다 이전이어야 합니다.")
        if applicants < 1 or applicants > self.settings.MAX_APPLICANTS:
            raise ValueError(f"응시자 수는 1 이상 {self.settings.MAX_APPLICANTS} 이하로 설정해야 합니다.")
