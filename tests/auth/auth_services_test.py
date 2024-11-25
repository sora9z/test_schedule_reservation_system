# https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.html#tests
import hashlib

import pytest

from app.common.constants import UserType
from app.common.database.models.user import User
from app.common.exceptions import AuthenticationError, DuplicateError
from app.common.respository.user_repository import AuthRepository
from app.config import Config
from app.schemas.user_schema import UserCreateRequest, UserCreateResponse, UserLoginRequest
from app.services.auth_service import AuthService


@pytest.fixture
def mock_auth_repository(mocker):
    return mocker.Mock(spec=AuthRepository)


@pytest.fixture
def mock_settings(mocker):
    return mocker.Mock(spec=Config)


def mock_create_access_token(mocker):
    return mocker.patch("app.common.utils.jwt.create_access_token")


def mock_create_refresh_token(mocker):
    return mocker.patch("app.common.utils.jwt.create_refresh_token")


@pytest.fixture
def auth_service(mock_auth_repository, mock_settings):
    return AuthService(repository=mock_auth_repository, settings=mock_settings)


@pytest.mark.asyncio
async def test_create_user_success(auth_service, mock_auth_repository):
    """
    [User] 사용자는 이메일과 비밀번호로 회원가입 할 수 있다.
    """
    # given
    input_data = UserCreateRequest(email="grep@grep.com", password="password", type=UserType.USER.value)
    mock_auth_create_user_repository_result = User(
        id=1,
        email="grep@grep.com",
        type=UserType.USER.value,
        hashed_password=hashlib.sha256("password".encode()).hexdigest(),
    )
    mock_auth_repository.get_user_by_email.return_value = None
    mock_auth_repository.create_user.return_value = mock_auth_create_user_repository_result
    # when
    result = await auth_service.create_user(data=input_data)

    # then
    assert result == UserCreateResponse.model_validate(mock_auth_create_user_repository_result)
    assert mock_auth_create_user_repository_result.email == input_data.email
    assert mock_auth_create_user_repository_result.type == UserType.USER.value
    assert mock_auth_create_user_repository_result.hashed_password == hashlib.sha256("password".encode()).hexdigest()


@pytest.mark.asyncio
async def test_create_user_fail_when_email_already_exists(auth_service, mock_auth_repository):
    """
    [User] 이미 존재하는 이메일로 회원가입 요청 시 예외가 발생한다.
    """
    # given
    input_data = UserCreateRequest(email="grep@grep.com", password="password", type=UserType.USER)
    mock_auth_repository.get_user_by_email.return_value = User(
        id=1,
        email="grep@grep.com",
        type=UserType.USER.value,
        hashed_password=hashlib.sha256("password".encode()).hexdigest(),
    )

    # when
    with pytest.raises(DuplicateError) as e:
        await auth_service.create_user(input_data)

    # then
    assert isinstance(e.value, DuplicateError)
    mock_auth_repository.create_user.assert_not_called()


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_auth_repository, mock_settings):
    """
    [User] 사용자는 이메일과 비밀번호로 로그인 할 수 있고, accessToken, refreshToken 을 발급받는다.
    """
    # given
    input_data = UserLoginRequest(email="grep@grep.com", password="password")
    mock_auth_repository.get_user_by_email.return_value = User(
        id=1,
        email="grep@grep.com",
        type=UserType.USER.value,
        hashed_password=hashlib.sha256("password".encode()).hexdigest(),
    )
    mock_settings.JWT_SECRET_KEY = "mocked_secret_key"
    mock_settings.JWT_ALGORITHM = "HS256"
    mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
    mock_settings.REFRESH_TOKEN_EXPIRE_MINUTES = 7
    mock_create_access_token.return_value = "mocked_access_token"
    mock_create_refresh_token.return_value = "mocked_refresh_token"

    # when
    result = await auth_service.login(data=input_data)

    # then
    assert result.access_token is not None
    assert result.refresh_token is not None


@pytest.mark.asyncio
async def test_login_fail_when_user_not_found(auth_service, mock_auth_repository):
    """
    [User] 존재하지 않는 계정인 경우 로그인할 수 없다. AuthenticationError 예외가 발생한다.
    """
    input_data = UserLoginRequest(email="grep@grep.com", password="password")
    mock_auth_repository.get_user_by_email.return_value = None

    # when
    with pytest.raises(AuthenticationError) as e:
        await auth_service.login(data=input_data)

    # then
    assert isinstance(e.value, AuthenticationError)


@pytest.mark.asyncio
async def test_login_fail_when_password_is_incorrect(auth_service, mock_auth_repository):
    """
    [User] 비밀번호가 일치하지 않는 경우 로그인할 수 없다. AuthenticationError 예외가 발생한다.
    """
    # given
    input_data = UserLoginRequest(email="grep@grep.com", password="password")
    mock_auth_repository.get_user_by_email.return_value = User(
        id=1,
        email="grep@grep.com",
        type=UserType.USER.value,
        hashed_password="hashed_password",
    )

    # when
    with pytest.raises(AuthenticationError) as e:
        await auth_service.login(data=input_data)

    # then
    assert isinstance(e.value, AuthenticationError)