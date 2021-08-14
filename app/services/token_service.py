"""Сервис для работы с зашифрованными данными."""

import datetime as dt

import jwt

import config
import exceptions


def create_course_invite_link(course_id):
    """Создание токена для приглашения в курс."""
    current_time = dt.datetime.utcnow()
    payload = {
        "iat": current_time,
        "exp": current_time + dt.timedelta(seconds=config.TOKEN_EXPIRATION),
        "course_id": course_id,
    }
    return jwt.encode(payload, config.SECRET_KEY, config.JWT_ALGORITHM)


async def get_course_id_from_token(request):
    """Получаем ID курса из пригласительного токена."""
    try:
        token = await fetch_token_from_request(request)
        token_data = jwt.decode(
            token,
            key=config.SECRET_KEY,
            algorithms=config.JWT_ALGORITHM,
        )
        course_id = token_data["course_id"]
    except Exception:
        raise exceptions.InvalidCourseInvite()
    else:
        return course_id


async def fetch_token_from_request(request):
    """Удостоверение пригласительного токена."""
    data = await request.json()
    invite = data["invite"]
    return invite


async def create_confirmation_token(request):
    """Создание токена для подтверждения регистрации."""
    data = await request.json()
    email = data["email"]
    username = data["username"]
    password = data["password"]
    role = data["role"]
    token = _create_confirmation_token(email, username, password, role)
    return email, token


def _create_confirmation_token(email, username, password, role):
    """Создание токена для подтверждения регистрации."""
    current_time = dt.datetime.utcnow()
    payload = {
        "iat": current_time,
        "exp": current_time
        + dt.timedelta(seconds=config.CONFIRMATION_TOKEN_EXPIRATION),
        "email": email,
        "username": username,
        "password": password,
        "role": role,
    }
    return jwt.encode(payload, config.SECRET_KEY, config.JWT_ALGORITHM)


async def check_is_register_data_correct(request):
    """Проверка правильности токена для подтверждения регистрации."""
    data = await request.json()
    confirmation_token = data.pop("confirmation_token")
    try:
        token_data = jwt.decode(
            confirmation_token,
            key=config.SECRET_KEY,
            algorithms=config.JWT_ALGORITHM,
        )
        token_data.pop("iat")
        token_data.pop("exp")
        assert data == token_data
    except Exception:
        return False
    else:
        return True
