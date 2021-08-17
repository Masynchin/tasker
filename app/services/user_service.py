"""Сервис для работы с пользователями."""

import tortoise.exceptions

from app import exceptions
from app.db.models import User


async def create_user(request):
    """Регистрация нового пользователя."""
    user = await _create_user_from_register_form(request)
    try:
        await user.save()
    except tortoise.exceptions.IntegrityError:
        raise exceptions.NotUniqueEmail()
    else:
        return user


async def _create_user_from_register_form(request):
    """Создание модели пользователя из данных формы регистрации."""
    form_data = await request.post()
    user = User(
        email=form_data["email"],
        username=form_data["username"],
    )
    user.set_password(form_data["password"])
    user.set_role(form_data["role"])
    return user


async def get_user(request):
    """Вход в аккаунт."""
    data = await request.post()
    email = data["email"]
    user = await User.get_or_none(email=email)
    if user is None:
        raise exceptions.UserDoesNotExist()

    password = data["password"]
    if not user.check_password(password):
        raise exceptions.IncorrectPassword()

    return user
