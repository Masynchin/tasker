from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import jinja2

import config
from db import init_db
from middlewares import setup_custom_middlewares
from routes import setup_routes
from views import AJAXHandler, FormHandler, SiteHandler, TokenHandler
from security import setup_security


async def create_app():
    """Инициализация приложения"""
    app = web.Application()
    aiohttp_jinja2.setup(
        app,
        enable_async=True,
        loader=jinja2.FileSystemLoader(config.TEMPLATES_PATH),
    )

    setup(app, EncryptedCookieStorage(config.SECRET_KEY))

    site_handler = SiteHandler()
    form_handler = FormHandler()
    ajax_handler = AJAXHandler()
    token_handler = TokenHandler()
    setup_routes(app, site_handler, form_handler, ajax_handler, token_handler)

    init_db(app)
    setup_security(app)
    setup_custom_middlewares(app)
    return app
