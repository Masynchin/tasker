import pytest

from app.db import init_test_db, close_test_db
from app.services import user_service


@pytest.fixture(autouse=True)
async def open_test_db():
    await init_test_db()
    yield
    await close_test_db()


@pytest.fixture
def create_user():
    async def _create_user(
        email=None, username=None, password=None, role=None
    ):
        user_data = {
            "email": email or "mail@mail.com",
            "username": username or "username",
            "password": password or "12345678",
            "role": role or "student",
        }
        await user_service.create_user(user_data)

    return _create_user
