"""Модуль с хэндлером приватных ссылок."""

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
import aiohttp_jinja2
from aiohttp_security import remember

from app import exceptions
from app.services import (
    create_user,
    create_confirmation_token,
    send_confirmation_email,
    get_register_token_data,
    get_course_id_from_token,
    subscribe_user_to_course_if_not_subscribed,
    get_course_by_id,
)
from app.utils import get_current_user, get_route


class TokenHandler:
    """Обработчик приватных ссылок."""

    async def create_token_confirmation(self, request: Request) -> Response:
        """Обработка запроса на создание токена удостоверения регистрации."""
        email, token = await create_confirmation_token(request)
        confirm_url = make_register_confirm_url(request, token)
        await send_confirmation_email(email, confirm_url)
        return web.json_response({"email": email})

    @aiohttp_jinja2.template("register_confirm.html")
    async def handle_register_token(self, request: Request) -> Response:
        """Обработка токена регистрации по ссылке из письма."""
        user = await get_current_user(request)
        if user.is_authenticated:
            return {"user": user}

        try:
            token_data = get_register_token_data(request)
            user = await create_user(token_data)
        except exceptions.InvalidRegisterToken:
            return {"user": user, "is_incorrect_token": True}
        except exceptions.NotUniqueEmail:
            return {"user": user, "is_incorrect_email": True}
        else:
            redirect_response = web.HTTPFound("/register/hello")
            await remember(request, redirect_response, str(user.id))
            return redirect_response

    async def confirm_course_invite(self, request: Request) -> Response:
        """Подтверждение правильности пригласительного токена.

        Если токен правильный, то пользователь автоматически
        подписывается на данный курс
        """
        try:
            user = await get_current_user(request)
            course_id = await get_course_id_from_token(request)
            course = await get_course_by_id(course_id)
        except exceptions.InvalidCourseInvite:
            return web.json_response({"error": "Неверное приглашение"})
        except exceptions.CourseDoesNotExist:
            return web.json_response(
                {"error": "Приглашение ведёт на несуществующий курс"},
            )
        else:
            await subscribe_user_to_course_if_not_subscribed(user, course)
            return web.json_response({"courseId": course.id})


def make_register_confirm_url(request: Request, token: str) -> str:
    """Создание ссылки для подтверждения регистрации."""
    route = get_route(request, "handle_register_token", token=token)
    confirm_url = f"{request.scheme}://{request.host}{route}"
    return confirm_url
