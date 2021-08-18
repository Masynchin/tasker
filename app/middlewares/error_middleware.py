"""Middleware для обработки выброшенных исключений.

Этот middleware обрабатывает исключения, выброшенные нашим сервером.
Это могут быть как намеренные исключения (исключеия aiohttp.web),
так и неотловленные самим сервером исключения.
"""

from typing import Awaitable, Callable

from aiohttp import web
import aiohttp_jinja2

from app.logger import logger
from app.utils import get_current_user


ERROR_DESCRIPTIONS = {
    403: "Похоже, что у вас нет доступа к этому содержимому",
    404: (
        "Огромная ошибка, не так ли? Сайт же не настолько большой, "
        "и такой ссылки мы найти не смогли :("
    ),
    500: "Похоже, что-то пошло не так",
}


Handler = Callable[[web.Request], Awaitable[web.Response]]


@web.middleware
async def error_middleware(
    request: web.Request, handler: Handler
) -> web.Response:
    """Обработка ошибок по типу 404, 500 и т.д."""
    try:
        response = await handler(request)
    except web.HTTPClientError as e:
        response = await render_error_template(request, e.status_code)
    except Exception:
        logger.exception("Произошла непредвиденная ошибка!")
        response = await render_error_template(request, 500)
    finally:
        return response  # noqa: B012


async def render_error_template(
    request: web.Request, error_code: int
) -> web.Response:
    """Рендер шаблона при ошибке на сайте."""
    user = await get_current_user(request)
    error_description = ERROR_DESCRIPTIONS[error_code]
    response = await aiohttp_jinja2.render_template_async(
        template_name="error_page.html",
        request=request,
        context={
            "user": user,
            "error_code": error_code,
            "error_description": error_description,
        },
    )
    return response
