"""Пакет со всеми путями приложения."""

import itertools

from app.views import course_handler
from app.views import index_hander
from app.views import lesson_handler
from app.views import solution_handler
from app.views import task_handler
from app.views import token_handler
from app.views import user_handler


routes = itertools.chain(
    course_handler.routes,
    index_hander.routes,
    lesson_handler.routes,
    solution_handler.routes,
    task_handler.routes,
    token_handler.routes,
    user_handler.routes,
)
