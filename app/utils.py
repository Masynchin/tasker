"""Модуль с разными полезными функциями."""

from typing import Union

from aiohttp.web import Request
from aiohttp_security import authorized_userid

from app.db.models import AnonimousUser, User
from yarl import URL


async def get_current_user(request: Request) -> Union[User, AnonimousUser]:
    """Обёртка над authorized_userid.

    При анонимном доступе, функция (authorized_userid) возвращает None,
    поэтому нужно её перехватывать и заменять None на экземляр AnonimousUser.
    """
    user = await authorized_userid(request)
    if user is None:
        user = AnonimousUser()
    return user


def get_route(request: Request, route: str, **params) -> URL:
    """Обёртка над request.app.router[...].url_for(...)."""
    return request.app.router[route].url_for(**params)
