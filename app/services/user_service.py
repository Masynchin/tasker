import hashlib

from aiohttp_security import remember, forget
from tortoise.exceptions import IntegrityError

import exceptions
from db.models import User
from db.models.user import UserRole


async def register_user(request, redirect_response):
    """Регистрация нового пользователя"""
    data = await request.post()
    username = data["username"]
    password_hash = _make_password_hash(data["password"])
    email = data["email"]
    role = UserRole.get_by_role_name(data["role"])
    try:
        user = await User.create(
            email=email,
            username=username,
            password_hash=password_hash,
            role=role,
        )
        await remember(request, redirect_response, str(user.id))
    except IntegrityError:
        raise exceptions.NotUniqueEmail()


async def login_user(request, redirect_response):
    """Вход в аккаунт"""
    data = await request.post()
    email = data["email"]
    user = await User.get_or_none(email=email)
    if user is None:
        raise exceptions.UserDoesNotExist()

    password = data["password"]
    if not _check_password_hash(password, user.password_hash):
        raise exceptions.IncorrectPassword()

    await remember(request, redirect_response, str(user.id))


async def logout_user(request, redirect_response):
    """Выход из аккаунта"""
    await forget(request, redirect_response)


def _make_password_hash(password):
    """Создание хэша для пароля пользователя"""
    return hashlib.sha256(password.encode("u8")).hexdigest()


def _check_password_hash(password, password_hash):
    """Проверка на совпадение пароля с хэшэм пароля пользователя"""
    return _make_password_hash(password) == password_hash
