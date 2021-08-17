"""Пакет с функцией установки соединения к БД."""

from tortoise import Tortoise
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


async def init_test_db():
    """Инициализация БД для тестов."""
    await Tortoise.init(
        db_url="sqlite://:memory:", modules={"models": ["app.db.models"]}
    )
    await Tortoise.generate_schemas()


async def close_test_db():
    """Закрытие БД для тестов."""
    await Tortoise.close_connections()
