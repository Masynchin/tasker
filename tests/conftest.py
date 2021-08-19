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
    async def _create_user(email, username, password, role):
        user_data = {
            "email": email,
            "username": username,
            "password": password,
            "role": role,
        }
        await user_service.create_user(user_data)

    return _create_user
