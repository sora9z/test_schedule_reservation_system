from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import ENUM as SQLEnum

from app.common.constants import UserType
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    type = Column(SQLEnum(UserType), default=UserType.USER)
    is_active = Column(Boolean, default=True)
