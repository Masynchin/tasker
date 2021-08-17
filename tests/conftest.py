import pytest

from app.db import init_test_db, close_test_db
from app.services import user_service


@pytest.fixture(autouse=True)
async def open_test_db():
    await init_test_db()
    yield
    await close_test_db()


class EmulatedFormRequest:
    def __init__(self, form_data):
        self.form_data = form_data

    async def post(self):
        return self.form_data


@pytest.fixture
def emulate_form_request():
    def _emulate_form_request(**form_data):
        return EmulatedFormRequest(form_data)

    return _emulate_form_request


@pytest.fixture
def create_user(emulate_form_request):
    async def _create_user(email, username, password, role):
        request = emulate_form_request(
            email=email, username=username, password=password, role=role
        )
        await user_service.create_user(request)

    return _create_user
