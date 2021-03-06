"""Собственная система авторизации."""

from aiohttp.web import Application
from aiohttp_security import (
    setup as _setup_security,
    SessionIdentityPolicy,
)
from aiohttp_security import authorized_userid  # noqa: F401
from aiohttp_security.abc import AbstractAuthorizationPolicy

from app.db.models import User


class UserAuthorizationPolicy(AbstractAuthorizationPolicy):
    """Создание собственной политики авторизации.

    Пример: https://aiohttp-security.readthedocs.io/en/latest/example.html.
    """

    async def authorized_userid(self, identity):  # noqa: F811
        """Получение модели пользователя по его identity."""
        user = await User.get_or_none(id=int(identity))
        return user

    async def permits(self, identity, permission, context=None):
        """Проверка прав доступа пользователя."""
        return True


def setup_security(app: Application):
    """Регистрация идентификационной политики."""
    policy = SessionIdentityPolicy()
    user_policy = UserAuthorizationPolicy()
    _setup_security(app, policy, user_policy)
