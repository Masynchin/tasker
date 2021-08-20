import pytest

from app.db import init_test_db, close_test_db
from app.services import course_service
from app.services import user_service


@pytest.fixture(autouse=True)
async def open_test_db():
    await init_test_db()
    yield
    await close_test_db()


@pytest.fixture
def unique_email():
    prefix = "a"

    def _unique_email():
        nonlocal prefix
        prefix = chr(ord(prefix) + 1)
        return f"{prefix}@mail.com"

    return _unique_email


@pytest.fixture
def create_user(unique_email):
    async def _create_user(
        email=None, username=None, password=None, role=None
    ):
        user_data = {
            "email": email or unique_email(),
            "username": username or "username",
            "password": password or "12345678",
            "role": role or "student",
        }
        return await user_service.create_user(user_data)

    return _create_user


@pytest.fixture
def create_course(create_user):
    async def _create_course(
        title=None, description=None, is_private=False, teacher=None
    ):
        course_data = {
            "title": title or "title",
            "description": description or "description",
        }
        if is_private:
            course_data["isPrivate"] = True

        teacher = teacher or (await create_user(role="teacher"))
        return await course_service.create_course(course_data, teacher)

    return _create_course
