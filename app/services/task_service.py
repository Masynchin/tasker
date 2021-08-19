"""Сервис для работы с задачи."""

from aiohttp.web import Request

from app import exceptions
from app.db.models import Lesson, Task, TaskSolution, User
from app.services.course_service import (
    is_course_teacher,
    raise_for_course_access,
)
from app.services.lesson_service import _get_lesson_by_id


async def create_task(request: Request, user: User) -> Task:
    """Создание задачи в уроке."""
    if not await is_course_teacher(request, user):
        raise exceptions.NotEnoughAccessRights()

    lesson_id = request.match_info["lesson_id"]
    lesson = await _get_lesson_by_id(lesson_id)
    order_index = await _get_order_index(lesson)

    data = await request.post()
    title = data["title"]
    condition = data["condition"]
    example = data["example"]
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
    return {
        "user": user,
        "task": task,
        "solution": solution,
    }


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


async def _get_task_solution(task: Task, user: User) -> dict:
    """Получение решения задачи, если таковое имеется."""
    solution_data = await (
        TaskSolution.get_or_none(task=task, student=user).values(
            "extension", "content", "status"
        )
    )
    if solution_data:
        (solution_data,) = solution_data
    return solution_data


async def handle_task_solution_request(
    task_id: int, solution_data: dict, user: User
):
    """Обработка запроса с решением задачи."""
    if not user.is_authenticated or user.is_teacher:
        raise exceptions.NotEnoughAccessRights()

    content = solution_data["content"].strip()
    extension = solution_data["extension"]
    task = await _get_task_by_id(task_id)

    solution = await TaskSolution.get_or_none(student=user, task=task)
    if solution is not None:
        await solution.delete()

    await TaskSolution.create(
        content=content,
        extension=extension,
        student=user,
        task=task,
    )
