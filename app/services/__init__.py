"""Пакет со всеми функциями наших сервисов.

Функции импортируются, чтобы в хэндлерах можно было делать
`from services import ...`.
"""

from services.course_service import *
from services.email_service import *
from services.lesson_service import *
from services.solution_service import *
from services.task_service import *
from services.token_service import *
from services.user_service import *
