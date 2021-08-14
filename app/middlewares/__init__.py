"""Пакет с фукнцией для установки наших middleware."""

from middlewares.error_middleware import error_middleware


def setup_custom_middlewares(app):
    """Установка собственных middleware."""
    app.middlewares.append(error_middleware)
