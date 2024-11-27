import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.common.database.models.reservation import Reservation

logger = logging.getLogger(__name__)


class ReservationRepository:
    def __init__(self, session_factory: async_scoped_session) -> None:
        self.session_factory = session_factory

    async def create_reservation_with_external_session(
        self, reservation: Reservation, session: AsyncSession
    ) -> Reservation:
        return await self._create_reservation(reservation, session)

    async def _create_reservation(self, reservation: Reservation, session: AsyncSession) -> Reservation:
        try:
            session.add(reservation)
            await session.flush()
            return reservation
        except Exception as e:
            logger.error(f"[repository/reservation_repository] _create_reservation error: {e}")
            raise e

    async def get_reservations_by_user_id(self, user_id: int) -> List[Reservation]:
        async with self.session_factory() as session:
            query = select(Reservation).where(Reservation.user_id == user_id)
            reservations = await session.execute(query)
            return reservations.scalars().all()

    async def get_reservations(self) -> List[Reservation]:
        async with self.session_factory() as session:
            query = select(Reservation)
            reservations = await session.execute(query)
            return reservations.scalars().all()

    async def get_reservation_by_id_with_external_session(
        self, reservation_id: int, session: AsyncSession
    ) -> Reservation:
        query = await session.execute(select(Reservation).where(Reservation.id == reservation_id))
        return query.scalar_one_or_none()

    async def update_reservation_with_external_session(self, reservation: Reservation, session: AsyncSession):
        session.add(reservation)
        await session.flush()
        return reservation

    async def delete_reservation_with_external_session(self, reservation_id: int, session: AsyncSession):
        query = await session.execute(select(Reservation).where(Reservation.id == reservation_id))
        reservation = query.scalar_one_or_none()
        if reservation:
            await session.delete(reservation)
            await session.flush()
