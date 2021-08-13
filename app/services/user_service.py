from aiohttp_security import remember, forget
from tortoise.exceptions import IntegrityError

import exceptions
from db.models import User


async def register_user(request, redirect_response):
    """Регистрация нового пользователя"""
    user = await _create_user_from_register_form(request)
    try:
        await user.save()
        await remember(request, redirect_response, str(user.id))
    except IntegrityError:
        raise exceptions.NotUniqueEmail()


async def _create_user_from_register_form(request):
    """Создание модели пользователя из данных формы регистрации"""
    form_data = await request.post()
    user = User(
        email=form_data["email"],
        username=form_data["username"],
    )
    user.set_password(form_data["password"])
    user.set_role(form_data["role"])
    return user


async def login_user(request, redirect_response):
    """Вход в аккаунт"""
    data = await request.post()
    email = data["email"]
    user = await User.get_or_none(email=email)
    if user is None:
        raise exceptions.UserDoesNotExist()

    password = data["password"]
    if not user.check_password(password):
        raise exceptions.IncorrectPassword()

    await remember(request, redirect_response, str(user.id))


async def logout_user(request, redirect_response):
    """Выход из аккаунта"""
    await forget(request, redirect_response)
