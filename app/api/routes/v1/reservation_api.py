import datetime
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.common.auth.get_current_user import get_current_user
from app.container import Container
from app.schemas.reservation_schema import (
    AvailableReservationResponse,
    DeleteReservationResponse,
    ReservationCreateRequest,
    ReservationListResponse,
    ReservationResponse,
    ReservationUpdateRequest,
    ReservationUpdateResponse,
)
from app.services.reservation_service import ReservationService

logger = logging.getLogger(__name__)
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


@router.patch(
    "/{reservation_id}",
    response_model=ReservationUpdateResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_reservation(
    reservation_id: str,
    body: ReservationUpdateRequest,
    user_info: dict = Depends(get_current_user),
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> ReservationUpdateResponse:
    try:
        user_id = user_info["user_id"]
        user_type = user_info["type"]
        return await reservation_service.update_reservation(body, int(reservation_id), user_id, user_type)
    except Exception as e:
        logger.error(f"[api/reservation_api] update_reservation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{reservation_id}",
)
@inject
async def delete_reservation(
    reservation_id: str,
    user_info: dict = Depends(get_current_user),
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> DeleteReservationResponse:
    user_id = user_info["user_id"]
    user_type = user_info["type"]
    return await reservation_service.delete_reservation(int(reservation_id), user_id, user_type)
