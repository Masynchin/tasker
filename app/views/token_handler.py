"""Модуль с хэндлером приватных ссылок."""

from aiohttp import web

from app import exceptions
from app.services import (
    create_confirmation_token,
    send_confirmation_email,
    check_is_register_data_correct,
    get_course_id_from_token,
    subscribe_user_to_course_if_not_subscribed,
    get_course_by_id,
)
from app.utils import get_current_user


class TokenHandler:
    """Обработчик приватных ссылок."""

    async def create_token_confirmation(self, request):
        """Обработка запроса на создание токена удостоверения регистрации."""
        email, token = await create_confirmation_token(request)
        await send_confirmation_email(email, token)
        return web.json_response({"email": email})

    async def check_register_data_indentity(self, request):
        """Проверка совпадения токена с данными регистрационной формы."""
        is_correct = await check_is_register_data_correct(request)
        if is_correct:
            return web.json_response({})
        else:
            return web.json_response({"error": "Токен не совпадает с данными"})

    async def confirm_course_invite(self, request):
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
