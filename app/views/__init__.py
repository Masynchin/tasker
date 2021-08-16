"""Пакет со всеми хэндлерами.

Данные хэндлеры импортируются в routes.py для определения их путей.
"""

from app.views.ajax_handler import AJAXHandler
from app.views.form_handler import FormHandler
from app.views.site_handler import SiteHandler
from app.views.token_handler import TokenHandler


__all__ = (AJAXHandler, FormHandler, SiteHandler, TokenHandler)
