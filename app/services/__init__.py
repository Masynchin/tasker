"""Пакет со всеми функциями наших сервисов.

Функции импортируются, чтобы в хэндлерах можно было делать
`from app.services import ...`.
"""

from app.services.course_service import *
from app.services.email_service import *
from app.services.lesson_service import *
from app.services.solution_service import *
from app.services.task_service import *
from app.services.token_service import *
from app.services.user_service import *
