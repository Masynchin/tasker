"""Модуль с разными полезными функциями."""

from aiohttp_security import authorized_userid

from db.models import AnonimousUser


async def get_current_user(request):
    """Обёртка над authorized_userid.

    При анонимном доступе, функция (authorized_userid) возвращает None,
    поэтому нужно её перехватывать и заменять None на экземляр AnonimousUser.
    """
    user = await authorized_userid(request)
    if user is None:
        user = AnonimousUser()
    return user


def get_route(request, route, **params):
    """Обёртка над request.app.router[...].url_for(...)."""
    return request.app.router[route].url_for(**params)
