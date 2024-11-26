import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.container import Container
from app.schemas.reservation_schema import AvailableReservationResponse, ReservationCreateRequest, ReservationResponse
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
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> ReservationResponse:
    return await reservation_service.create_reservation(body)


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
