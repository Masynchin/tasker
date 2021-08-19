"""Сервис для работы с пользователями."""

import tortoise.exceptions

from app import exceptions
from app.db.models import User


async def create_user(user_data: dict) -> User:
    """Создание пользователя по данным."""
    user = _create_user_from_data(user_data)
    try:
        await user.save()
    except tortoise.exceptions.IntegrityError:
        raise exceptions.NotUniqueEmail()
    else:
        return user


def _create_user_from_data(data: dict) -> User:
    """Создание модели пользователя из данных."""
    user = User(
        email=data["email"],
        username=data["username"],
    )
    user.set_password(data["password"])
    user.set_role(data["role"])
    return user


async def get_user(email: str, password: str) -> User:
    """Получение пользователя по данным формы запроса."""
    user = await User.get_or_none(email=email)
    if user is None:
        raise exceptions.UserDoesNotExist()

    if not user.check_password(password):
        raise exceptions.IncorrectPassword()

    return user
