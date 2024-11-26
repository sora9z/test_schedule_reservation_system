import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.common.database.models.reservation import Reservation

logger = logging.getLogger(__name__)


class ReservationRepository:
    def __init__(self, session_factory: async_scoped_session) -> None:
        self.session_factory = session_factory

    async def create_reservation_with_external_session(self, reservation: dict, session: AsyncSession) -> Reservation:
        return await self._create_reservation(reservation, session)

    async def create_reservation(self, reservation: dict) -> Reservation:
        async with self.session_factory() as session:
            return await self._create_reservation(reservation, session)

    async def _create_reservation(self, reservation: dict, session: AsyncSession) -> Reservation:
        try:
            reservation = Reservation(**reservation)
            session.add(reservation)
            await session.flush()
            return reservation
        except Exception as e:
            logger.error(f"[repository/reservation_repository] _create_reservation error: {e}")
            raise e
