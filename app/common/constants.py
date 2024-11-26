from enum import Enum


class UserType(Enum):
    USER = "USER"
    ADMIN = "ADMIN"

    def __str__(self):
        return self.value


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"

    def __str__(self):
        return self.value
