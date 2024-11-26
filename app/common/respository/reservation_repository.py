import logging
from datetime import datetime
from typing import List

from sqlalchemy import func, select, types
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.common.constants import ReservationStatus
from app.common.database.models.reservation import Reservation

logger = logging.getLogger(__name__)


class ReservationRepository:
    def __init__(self, session_factory: async_scoped_session) -> None:
        self.session_factory = session_factory

    """
    겹치는 예약 조회
    start_time: 시작 시간
    end_time: 종료 시간
    range_type: 시간 범위 타입
    - '[]' : 시작 시간 ~ 종료 시간 포함
    - '()' : 시작 시간 ~ 종료 시간 미포함
    - '[)' : 시작 시간 포함, 종료 시간 미포함
    - '(]' : 시작 시간 미포함, 종료 시간 포함
    """

    async def get_overlapping_reservations_with_external_session(
        self, start_time: datetime, end_time: datetime, range_type: str, session: AsyncSession
    ) -> List[Reservation]:
        return await self._get_overlapping_reservations(start_time, end_time, range_type, session)

    async def get_overlapping_reservations(
        self,
        start_time: datetime,
        end_time: datetime,
        range_type: str,
    ) -> List[Reservation]:
        try:
            async with self.session_factory() as session:
                return await self._get_overlapping_reservations(start_time, end_time, range_type, session)
        except Exception as e:
            logger.error(f"[repository/reservation_repository] get_overlapping_reservations error: {e}")
            raise e

    async def create_reservation_with_external_session(self, reservation: dict, session: AsyncSession) -> Reservation:
        return await self._create_reservation(reservation, session)

    async def create_reservation(self, reservation: dict) -> Reservation:
        async with self.session_factory() as session:
            return await self._create_reservation(reservation, session)

    async def _get_overlapping_reservations(
        self, start_time: datetime, end_time: datetime, range_type: str, session: AsyncSession
    ) -> List[Reservation]:
        try:
            time_range = func.tstzrange(
                func.cast(start_time, types.TIMESTAMP(timezone=True)),
                func.cast(end_time, types.TIMESTAMP(timezone=True)),
                range_type,
            )
            stmt = select(Reservation).where(
                Reservation.status == ReservationStatus.PENDING.value, Reservation.time_range.op("&&")(time_range)
            )
            result = await session.execute(stmt)
            overlapping_reservations = result.scalars().all()
            return overlapping_reservations
        except Exception as e:
            logger.error(f"[repository/reservation_repository] _get_overlapping_reservations error: {e}")
            raise e

    async def _create_reservation(self, reservation: dict, session: AsyncSession) -> Reservation:
        try:
            reservation = Reservation(**reservation)
            session.add(reservation)
            await session.flush()
            return reservation
        except Exception as e:
            logger.error(f"[repository/reservation_repository] _create_reservation error: {e}")
            raise e
