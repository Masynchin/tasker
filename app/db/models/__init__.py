"""Пакет со всеми моделями.

Модели импортируются, чтобы можно было делать импорт в виде
`from app.db.models import ...`.
"""

from app.db.models.course import Course
from app.db.models.lesson import Lesson
from app.db.models.task import Task
from app.db.models.task_solution import TaskSolution
from app.db.models.user import User, AnonimousUser


__all__ = (
    Course,
    Lesson,
    Task,
    TaskSolution,
    User,
    AnonimousUser,
)
