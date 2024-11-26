from fastapi import APIRouter

from app.api.routes.v1 import reservation_api as reservation_v1
from app.api.routes.v1 import user_api as user_v1

router = APIRouter(tags=["API"], prefix="/api")

router.include_router(user_v1.router, tags=["user"])
router.include_router(reservation_v1.router, tags=["reservation"])
