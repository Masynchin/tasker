import pytest

from app import exceptions
from app.services import user_service


@pytest.mark.asyncio
async def test_create_user():
    user_data = {
        "email": "mail@mail.com",
        "username": "username",
        "role": "teacher",
        "password": "12345678",
    }
    user = await user_service.create_user(user_data)

    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.check_password(user_data["password"])

    with pytest.raises(exceptions.NotUniqueEmail):
        await user_service.create_user(user_data)


@pytest.mark.asyncio
async def test_login_user(create_user):
    email = "mail@mail.com"
    password = "12345678"
    await create_user(
        email=email,
        password=password,
        username="user",
        role="student",
    )

    user = await user_service.get_user(email, password)

    assert user.email == email
    assert user.check_password(password)

    non_existed_email = email + "not_exists@yet"
    with pytest.raises(exceptions.UserDoesNotExist):
        await user_service.get_user(non_existed_email, password)

    incorrect_password = password + "incorrect"
    with pytest.raises(exceptions.IncorrectPassword):
        await user_service.get_user(email, incorrect_password)
