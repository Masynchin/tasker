"""Модуль с хэндлерами путей пользователя."""

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Response, Request
from aiohttp_security import forget, remember

from app import exceptions
from app.services import get_user
from app.utils import get_current_user, get_route


routes = web.RouteTableDef()


@routes.get("/profile", name="profile")
@aiohttp_jinja2.template("profile.html")
async def profile(request: Request) -> Response:
    """Страница пользователя."""
    user = await get_current_user(request)
    if not user.is_authenticated:
        route = get_route(request, "register")
        return web.HTTPFound(location=route)
    return {"user": user}


@routes.get("/register", name="register")
@aiohttp_jinja2.template("register.html")
async def register(request: Request) -> Response:
    """Страница регистрации."""
    user = await get_current_user(request)
    if user.is_authenticated:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    return {"user": user}


@routes.get("/login", name="login")
@aiohttp_jinja2.template("login.html")
async def login(request: Request) -> Response:
    """Страница входа в аккаунт."""
    user = await get_current_user(request)
    if user.is_authenticated:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)
    return {"user": user}


@routes.post("/login")
async def handle_login(request: Request) -> Response:
    """Обработка данных для входа в аккаунт."""
    try:
        form_data = await request.post()
        email = form_data["email"]
        password = form_data["password"]
        route = get_route(request, "index")
        user = await get_user(email, password)
    except (exceptions.IncorrectPassword, exceptions.UserDoesNotExist):
        route = get_route(request, "login")
        return web.HTTPFound(location=route)
    else:
        redirect_response = web.HTTPFound(location=route)
        await remember(request, redirect_response, str(user.id))
        return redirect_response


@routes.get("/logout", name="logout")
async def logout(request: Request) -> Response:
    """Выход из аккаунта."""
    redirect_response = web.HTTPFound("/")
    await forget(request, redirect_response)
    return redirect_response
