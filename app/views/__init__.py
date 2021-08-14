"""Пакет со всеми хэндлерами.

Данные хэндлеры импортируются в routes.py для определения их путей.
"""

from views.ajax_handler import AJAXHandler
from views.form_handler import FormHandler
from views.site_handler import SiteHandler
from views.token_handler import TokenHandler


__all__ = (AJAXHandler, FormHandler, SiteHandler, TokenHandler)
