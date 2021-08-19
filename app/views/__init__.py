"""Пакет со всеми путями приложения."""

import itertools

from app.views import ajax_handler
from app.views import form_handler
from app.views import site_handler
from app.views import token_handler


routes = itertools.chain(
    ajax_handler.routes,
    form_handler.routes,
    site_handler.routes,
    token_handler.routes,
)
