"""Пакет со всеми моделями.

Модели импортируются, чтобы можно было делать импорт в виде
`from db.models import ...`.
"""

from db.models.course import Course
from db.models.lesson import Lesson
from db.models.task import Task
from db.models.task_solution import TaskSolution
from db.models.user import User, AnonimousUser


__all__ = (
    Course,
    Lesson,
    Task,
    TaskSolution,
    User,
    AnonimousUser,
)
