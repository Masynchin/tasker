"""Файл запуска сервера локально."""

from aiohttp import web

from app.main import create_app


web.run_app(create_app())
