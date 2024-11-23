# https://python-dependency-injector.ets-labs.org/examples/fastapi-sqlalchemy.html#tests
import pytest

from app.common.constants import UserType
from app.common.exceptions import DuplicateError
from app.common.respository.user_repository import AuthRepository
from app.services.auth_service import AuthService


@pytest.fixture
def mock_auth_repository(mocker):
    return mocker.Mock(spec=AuthRepository)


@pytest.fixture
def auth_service(mock_auth_repository):
    return AuthService(repository=mock_auth_repository)


@pytest.mark.asyncio
async def test_create_user_success(auth_service, mock_auth_repository):
    """
    [User] 사용자는 이메일과 비밀번호로 회원가입 할 수 있다.
    """
    # given
    mock_auth_repository.get_user_by_email.return_value = None
    mock_auth_repository.create_user.return_value = {
        "id": 1,
        "email": "grep@grep.com",
        "type": UserType.USER.value,
    }
    input_data = {"email": "grep@grep.com", "password": "password"}

    # when
    result = await auth_service.create_user(input_data)

    # then
    assert result == {"id": 1, "email": "grep@grep.com", "type": UserType.USER.value}
    mock_auth_repository.create_user.assert_called_once_with(input_data)


@pytest.mark.asyncio
async def test_create_user_fail_when_email_already_exists(auth_service, mock_auth_repository):
    """
    [User] 이미 존재하는 이메일로 회원가입 요청 시 예외가 발생한다.
    """
    # given
    mock_auth_repository.get_user_by_email.return_value = {
        "id": 1,
        "email": "grep@grep.com",
        "type": UserType.USER.value,
    }
    input_data = {"email": "grep@grep.com", "password": "password"}

    # when
    with pytest.raises(DuplicateError) as e:
        await auth_service.create_user(input_data)

    # then
    assert isinstance(e.value, DuplicateError)
    mock_auth_repository.create_user.assert_not_called()
