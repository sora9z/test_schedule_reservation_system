import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.common.auth.get_current_user import get_current_user
from app.container import Container
from app.schemas.reservation_schema import (
    AvailableReservationResponse,
    ReservationCreateRequest,
    ReservationListResponse,
    ReservationResponse,
)
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/v1/reservations")


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_reservation(
    body: ReservationCreateRequest,
    user_info: dict = Depends(get_current_user),
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> ReservationResponse:
    user_id = user_info["user_id"]
    return await reservation_service.create_reservation(body, user_id)


@router.get(
    "/available",
    response_model=AvailableReservationResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_available_reservation(
    date: datetime.date,
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> AvailableReservationResponse:
    return await reservation_service.get_available_reservation(date)


@router.get(
    "/",
    response_model=ReservationListResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_reservations(
    user_info: dict = Depends(get_current_user),
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> ReservationListResponse:
    user_id = user_info["user_id"]
    return await reservation_service.get_reservations_by_user(user_id)


@router.get(
    "/admin",
    response_model=ReservationListResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_reservations_by_admin(
    user_info: dict = Depends(get_current_user),
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> ReservationListResponse:
    user_type = user_info["type"]
    return await reservation_service.get_reservations_by_admin(user_type)
