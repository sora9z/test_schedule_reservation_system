# https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.html#endpoints
# https://python-dependency-injector.ets-labs.org/wiring.html#wiring
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.container import Container
from app.schemas.user_schema import UserCreateRequest, UserCreateResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/v1/users")


@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    body: UserCreateRequest, auth_service: AuthService = Depends(Provide[Container.auth_service])
) -> UserCreateResponse:
    return await auth_service.create_user(body)


# @inject
# async def create_user(
#     body: CreateUserInRequest, user_create_service: CreateUserService = Depends(Provide[Container.create_user_service])
# ) -> UserGetResponse:
#     return await user_create_service(create_user=body)
