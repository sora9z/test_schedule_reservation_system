from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, Table
from sqlalchemy.dialects.postgresql import ENUM, TSTZRANGE
from sqlalchemy.orm import relationship

from app.common.constants import ReservationStatus
from app.common.database.models.base import Base

# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#relationships-many-to-many
reservation_slots = Table(
    "reservation_slots",
    Base.metadata,
    Column("reservation_id", Integer, ForeignKey("reservations.id"), primary_key=True),
    Column("slot_id", Integer, ForeignKey("slots.id"), primary_key=True),
)
# TODO 사용하지 않는 컬럼 제거


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    exam_start_date = Column(DateTime, nullable=False)
    exam_end_date = Column(DateTime, nullable=False)
    applicants = Column(Integer, nullable=False)
    status = Column(ENUM(ReservationStatus, name="reservation_status"), default=ReservationStatus.PENDING.value)

    time_range = Column(TSTZRANGE, nullable=False)  # 시험 시작 시간 ~ 종료 시간 검색을 위한 컬럼

    user = relationship("User", back_populates="reservations")
    slots = relationship("Slot", secondary=reservation_slots, back_populates="reservations")

    __table_args__ = (
        Index("idx_reservations_time_range", "time_range", postgresql_using="gist"),
        Index("idx_reservations_exam_date", "exam_date"),
        CheckConstraint("exam_end_date > exam_start_date", name="check_exam_time_valid"),
    )
