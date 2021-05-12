from aiohttp import web, web_exceptions
import aiohttp_jinja2

from logger import logger
from utils import get_current_user


ERROR_DESCRIPTIONS = {
    404: "Огромная ошибка, не так ли? Сайт же не настолько большой, "
         "и такой ссылки мы найти не смогли :(",
    500: "Похоже, что-то пошло не так",
}


@web.middleware
async def error_middleware(request, handler):
    """Обработка ошибок по типу 404, 500 и т.д."""
    try:
        response = await handler(request)
    except web_exceptions.HTTPClientError as e:
        response = await render_error_template(request, e.status_code)
    except Exception as e:
        logger.exception("Произошла непредвиденная ошибка!")
        response = await render_error_template(request, 500)
    finally:
        return response


async def render_error_template(request, error_code):
    """Рендер шаблона при ошибке на сайте"""
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
