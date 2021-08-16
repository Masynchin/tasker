"""Модуль с функцией создания приложения.

Данная фукнция импортируется в __init__.py.
"""

from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import setup as setup_sessions
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import jinja2

from app import config
from app.db import setup_db
from app.middlewares import setup_custom_middlewares
from app.routes import setup_routes
from app.security import setup_security


async def create_app():
    """Инициализация приложения."""
    app = web.Application()
    aiohttp_jinja2.setup(
        app,
        enable_async=True,
        loader=jinja2.FileSystemLoader(config.TEMPLATES_PATH),
    )

    setup_sessions(app, EncryptedCookieStorage(config.SECRET_KEY))
    setup_routes(app)
    setup_security(app)
    setup_custom_middlewares(app)
    setup_db(app)
    return app
