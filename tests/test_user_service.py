import pytest

from app import exceptions
from app.services import user_service


@pytest.mark.asyncio
async def test_create_user(emulate_form_request):
    form_data = {
        "email": "mail@mail.com",
        "username": "username",
        "role": "teacher",
        "password": "12345678",
    }
    request = emulate_form_request(**form_data)

    user = await user_service.create_user(request)

    assert user.email == form_data["email"]
    assert user.username == form_data["username"]
    assert user.check_password(form_data["password"])

    with pytest.raises(exceptions.NotUniqueEmail):
        await user_service.create_user(request)


@pytest.mark.asyncio
async def test_login_user(create_user, emulate_form_request):
    email = "mail@mail.com"
    password = "12345678"
    await create_user(
        email=email,
        password=password,
        username="user",
        role="student",
    )

    request = emulate_form_request(email=email, password=password)
    user = await user_service.get_user(request)

    assert user.email == email
    assert user.check_password(password)

    non_existed_email = email + "not_exists@yet"
    request = emulate_form_request(email=non_existed_email, password=password)
    with pytest.raises(exceptions.UserDoesNotExist):
        await user_service.get_user(request)

    incorrect_password = password + "incorrect"
    request = emulate_form_request(email=email, password=incorrect_password)
    with pytest.raises(exceptions.IncorrectPassword):
        await user_service.get_user(request)
