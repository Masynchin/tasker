from aiohttp_security import (
    setup as _setup_security,
    authorized_userid,
    SessionIdentityPolicy,
)
from aiohttp_security.abc import AbstractAuthorizationPolicy

from db.models import User


class UserAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):  # noqa: F811
        """Получение модели пользователя по его identity"""
        user = await User.get_or_none(id=int(identity))
        return user

    async def permits(self, identity, permission, context=None):
        """Проверка прав доступа пользователя"""
        return True


def setup_security(app):
    """Регистрация идентификационной политики"""
    policy = SessionIdentityPolicy()
    user_policy = UserAuthorizationPolicy()
    _setup_security(app, policy, user_policy)
