"""Сервис для работы с задачи."""

from typing import TypedDict

from app import exceptions
from app.db.models import Lesson, Task, TaskSolution, User
from app.db.models.task_solution import TaskSolutionStatus
from app.services.course_service import (
    is_course_teacher,
    get_course_by_id,
    raise_for_course_access,
)
from app.services.lesson_service import _get_lesson_by_id


class TaskSolutionData(TypedDict):
    """Модель данных решения задачи."""

    extension: str
    content: str
    status: TaskSolutionStatus


async def create_task(
    course_id: int, lesson_id: int, task_data: dict, user: User
) -> Task:
    """Создание задачи в уроке."""
    course = await get_course_by_id(course_id)
    if not await is_course_teacher(course, user):
        raise exceptions.NotEnoughAccessRights()

    lesson = await _get_lesson_by_id(lesson_id)
    order_index = await _get_order_index(lesson)

    title = task_data["title"]
    condition = task_data["condition"]
    example = task_data["example"]
    task = await Task.create(
        title=title,
        condition=condition,
        example=example,
        order_index=order_index,
        lesson=lesson,
    )
    return task


async def _get_order_index(lesson: Lesson) -> int:
    """Получение порядкового номера для новой задачи."""
    tasks = await lesson.tasks
    return len(tasks)


async def get_task_page_data(task_id: int, user: User) -> dict:
    """Получение данных для шаблона страницы задачи в виде JSON."""
    task = await _get_task_by_id(task_id)
    await _raise_for_task_access(task, user)
    solution = await _get_task_solution(task, user)
    return {"task": task, "solution": solution}


async def _get_task_by_id(task_id: int) -> Task:
    """Получение задачи по её ID."""
    task = await Task.get_or_none(id=task_id)
    if task is None:
        raise exceptions.TaskDoesNotExist()

    return task


async def _raise_for_task_access(task: Task, user: User):
    """Выбрасываем ошибку, если курс закрытый и пользователь в нём нет."""
    lesson = await task.lesson
    course = await lesson.course
    await raise_for_course_access(course, user)


async def _get_task_solution(task: Task, user: User) -> TaskSolutionData:
    """Получение решения задачи, если таковое имеется."""
    solution_data = await (
        TaskSolution.get_or_none(task=task, student=user).values(
            "extension", "content", "status"
        )
    )
    if solution_data:
        (solution_data,) = solution_data

    return solution_data
