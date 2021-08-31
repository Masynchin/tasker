"""Модуль с хэндлером главной страницы."""

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Response, Request

from app.services import get_user_courses
from app.utils import get_current_user


routes = web.RouteTableDef()


@routes.get("/", name="index")
@aiohttp_jinja2.template("home.html")
async def index(request: Request) -> Response:
    """Главная страница."""
    user = await get_current_user(request)
    courses = await get_user_courses(user)
    return {"user": user, "courses": courses}
