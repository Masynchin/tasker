from tortoise.contrib.aiohttp import register_tortoise

import config


def init_db(app):
    """Инициализация базы данных"""
    register_tortoise(
        app,
        db_url=config.DATABASE_URL,
        modules={"models": ["db.models"]},
        generate_schemas=True,
    )
