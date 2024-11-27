import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.common.auth.get_current_user import get_current_user
from app.container import Container
from app.schemas.reservation_schema import ConfirmReservationResponse, ReservationListResponse
from app.services.reservation_service import ReservationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin")


@router.patch(
    "/reservations/{reservation_id}/confirm",
    response_model=ConfirmReservationResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def confirm_reservation(
    reservation_id: int,
    user_info: dict = Depends(get_current_user),
    reservation_service: ReservationService = Depends(Provide[Container.reservation_service]),
) -> ConfirmReservationResponse:
    try:
        response = await reservation_service.confirm_reservations(reservation_id, user_info["type"])
        logger.info(f"Reservation {reservation_id} confirmed successfully.")
        return response
    except Exception as e:
        logger.error(f"Error confirming reservation {reservation_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/reservations",
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
