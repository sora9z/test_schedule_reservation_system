from sqlalchemy import Column, Date, Index, Integer, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.orm import relationship

from app.common.database.models.base import Base
from app.config import settings


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    time_range = Column(TSTZRANGE, nullable=False)
    remaining_capacity = Column(Integer, nullable=False, default=settings.MAX_APPLICANTS)

    reservations = relationship("Reservation", secondary="reservation_slots", back_populates="slots")

    __table_args__ = (
        UniqueConstraint("date", "start_time", "end_time", name="unique_slot"),
        Index("idx_slots_time_range", "time_range", postgresql_using="gist"),
    )
