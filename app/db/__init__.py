"""Пакет с функцией установки соединения к БД."""

from tortoise.contrib.aiohttp import register_tortoise

from app import config


def setup_db(app):
    """Инициализация базы данных."""
    register_tortoise(
        app,
        db_url=config.DATABASE_URL,
        modules={"models": ["app.db.models"]},
        generate_schemas=True,
    )
