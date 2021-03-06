"""Модуль с хэндлерами приватных ссылок."""

from aiohttp import web
from aiohttp.web import Response, Request
import aiohttp_jinja2
from aiohttp_security import remember

from app import exceptions
from app.services import (
    create_user,
    create_confirmation_token,
    send_confirmation_email,
    get_register_token_data,
    get_course_id_from_token,
    subscribe_user_to_course,
    get_course_by_id,
)
from app.utils import get_current_user, get_route


routes = web.RouteTableDef()


@routes.post("/create_token_confirmation")
async def create_token_confirmation(request: Request) -> Response:
    """Обработка запроса на создание токена удостоверения регистрации."""
    register_data = await request.json()
    email = register_data["email"]
    token = create_confirmation_token(register_data)
    confirm_url = make_register_confirm_url(request, token)
    await send_confirmation_email(email, confirm_url)
    return web.json_response({"email": email})


@routes.get(r"/register/{token}", name="handle_register_token")
@aiohttp_jinja2.template("register_confirm.html")
async def handle_register_token(request: Request) -> Response:
    """Обработка токена регистрации по ссылке из письма."""
    user = await get_current_user(request)
    if user.is_authenticated:
        return {"user": user}

    try:
        token = request.match_info["token"]
        token_data = get_register_token_data(token)
        user = await create_user(token_data)
    except exceptions.InvalidRegisterToken:
        return {"user": user, "is_incorrect_token": True}
    except exceptions.NotUniqueEmail:
        return {"user": user, "is_incorrect_email": True}
    else:
        redirect_response = web.HTTPFound("/register/hello")
        await remember(request, redirect_response, str(user.id))
        return redirect_response


@routes.get("/activate_course_invite", name="activate_course_invite")
@aiohttp_jinja2.template("activate_course_invite.html")
async def activate_course_invite(request: Request) -> Response:
    """Страница активации пригласительного токена."""
    user = await get_current_user(request)
    if not user.is_authenticated or user.is_teacher:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    return {"user": user}


@routes.post("/confirm_course_invite")
async def confirm_course_invite(request: Request) -> Response:
    """Подтверждение правильности пригласительного токена.

    Если токен правильный, то пользователь автоматически
    подписывается на данный курс
    """
    user = await get_current_user(request)
    invite_token = (await request.json())["invite"]

    try:
        course_id = get_course_id_from_token(invite_token)
        course = await get_course_by_id(course_id)
    except exceptions.InvalidCourseInvite:
        return web.json_response({"error": "Неверное приглашение"})
    except exceptions.CourseDoesNotExist:
        return web.json_response(
            {"error": "Приглашение ведёт на несуществующий курс"},
        )
    else:
        await subscribe_user_to_course(user, course)
        return web.json_response({"courseId": course.id})


def make_register_confirm_url(request: Request, token: str) -> str:
    """Создание ссылки для подтверждения регистрации."""
    route = get_route(request, "handle_register_token", token=token)
    confirm_url = f"{request.scheme}://{request.host}{route}"
    return confirm_url
