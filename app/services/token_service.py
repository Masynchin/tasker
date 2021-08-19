"""Сервис для работы с зашифрованными данными."""

import datetime as dt

from aiohttp.web import Request
import jwt

from app import config
from app import exceptions


def create_course_invite_link(course_id: int) -> str:
    """Создание токена для приглашения в курс."""
    current_time = dt.datetime.utcnow()
    payload = {
        "iat": current_time,
        "exp": current_time + dt.timedelta(seconds=config.TOKEN_EXPIRATION),
        "course_id": course_id,
    }
    return jwt.encode(payload, config.SECRET_KEY, config.JWT_ALGORITHM)


async def get_course_id_from_token(request: Request) -> int:
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


async def fetch_token_from_request(request: Request) -> str:
    """Удостоверение пригласительного токена."""
    data = await request.json()
    invite = data["invite"]
    return invite


def create_confirmation_token(register_data: dict) -> str:
    """Создание токена для подтверждения регистрации."""
    current_time = dt.datetime.utcnow()
    payload = {
        "iat": current_time,
        "exp": current_time
        + dt.timedelta(seconds=config.CONFIRMATION_TOKEN_EXPIRATION),
        "email": register_data["email"],
        "username": register_data["username"],
        "password": register_data["password"],
        "role": register_data["role"],
    }
    return jwt.encode(payload, config.SECRET_KEY, config.JWT_ALGORITHM)


def get_register_token_data(request: Request) -> dict:
    """Получение данных из токена регистрации."""
    token = request.match_info["token"]
    try:
        token_data = jwt.decode(
            token,
            key=config.SECRET_KEY,
            algorithms=config.JWT_ALGORITHM,
        )
        token_data.pop("iat")
        token_data.pop("exp")
    except Exception:
        raise exceptions.InvalidRegisterToken()
    else:
        return token_data
