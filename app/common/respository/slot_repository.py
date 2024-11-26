import logging
from datetime import datetime
from typing import List

from sqlalchemy import func, select, types
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.common.database.models.slot import Slot

logger = logging.getLogger(__name__)


class SlotRepository:
    def __init__(self, session_factory: async_scoped_session) -> None:
        self.session_factory = session_factory

    """
    해당 시간대에 겹치는 슬롯 조회
    start_time: 시작 시간
    end_time: 종료 시간
    range_type: 시간 범위 타입
    - '[]' : 시작 시간 ~ 종료 시간 포함
    - '()' : 시작 시간 ~ 종료 시간 미포함
    - '[)' : 시작 시간 포함, 종료 시간 미포함
    - '(]' : 시작 시간 미포함, 종료 시간 포함
    """

    async def get_overlapping_slots_with_external_session(
        self,
        start_time: datetime,
        end_time: datetime,
        range_type: str,
        session: AsyncSession,
    ) -> List[Slot]:
        try:
            time_range = func.tstzrange(
                func.cast(start_time, types.TIMESTAMP(timezone=True)),
                func.cast(end_time, types.TIMESTAMP(timezone=True)),
                range_type,
            )
            stmt = select(Slot).where(Slot.time_range.op("&&")(time_range))
            result = await session.execute(stmt)
            overlapping_slots = result.scalars().all()
            return overlapping_slots
        except Exception as e:
            logger.error(f"[repository/slot_repository] get_overlapping_slots_with_external_session error: {e}")
            raise e

    async def get_available_slots(self, exam_date: datetime.date) -> List[Slot]:
        try:
            async with self.session_factory() as session:
                slots = await session.scalars(select(Slot).where(Slot.date == exam_date, Slot.remaining_capacity > 0))
                return slots
        except Exception as e:
            logger.error(f"[repository/slot_repository] get_available_slots error: {e}")
            raise e
