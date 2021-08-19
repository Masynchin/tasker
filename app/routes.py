"""Модуль с функцией регистрации путей."""

from aiohttp.web import Application

from app import config
from app.views import routes


def setup_routes(app: Application):
    """Регистрация путей."""
    app.add_routes(routes)
    app.router.add_static("/static/", path=config.STATIC_PATH, name="static")
