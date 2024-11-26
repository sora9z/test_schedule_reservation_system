from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.common.constants import UserType
from app.common.database.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    type = Column(
        ENUM(UserType, name="user_type", create_type=True),
        default=UserType.USER.value,
    )

    reservations = relationship("Reservation", back_populates="user", lazy="dynamic")
