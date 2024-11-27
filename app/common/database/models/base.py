from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.functions import current_timestamp


class Base(DeclarativeBase):
    created_at = Column(DateTime(timezone=True), default=current_timestamp(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=current_timestamp(), onupdate=current_timestamp(), nullable=False
    )
