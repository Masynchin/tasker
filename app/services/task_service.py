"""Сервис для работы с задачи."""

from aiohttp.web_request import Request

from app import exceptions
from app.db.models import Lesson, Task, TaskSolution, User
from app.services.course_service import (
    is_course_teacher,
    raise_for_course_access,
)
from app.services.lesson_service import get_lesson_from_request


async def create_task(request: Request, user: User) -> Task:
    """Создание задачи в уроке."""
    if not await is_course_teacher(request, user):
        raise exceptions.NotEnoughAccessRights()

    lesson = await get_lesson_from_request(request)
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


async def get_task_page_data(request: Request, user: User) -> dict:
    """Получение данных для шаблона страницы задачи в виде JSON."""
    task = await get_task_from_request(request)
    await _raise_for_task_access(task, user)
    solution = await _get_task_solution(task, user)
    lesson_id = request.match_info["lesson_id"]
    course_id = request.match_info["course_id"]
    return {
        "user": user,
        "task": task,
        "solution": solution,
        "lesson_id": lesson_id,
        "course_id": course_id,
    }


async def get_task_from_request(request: Request) -> Task:
    """Получение задачи по ID из запроса."""
    task_id = request.match_info["task_id"]
    task = await _get_task_by_id(task_id)
    return task


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


async def handle_task_solution_request(request: Request, user: User):
    """Обработка запроса с решением задачи."""
    if not user.is_authenticated or user.is_teacher:
        raise exceptions.NotEnoughAccessRights()

    data = await request.json()
    content = data["content"].strip()
    extension = data["extension"]
    task = await get_task_from_request(request)

    solution = await TaskSolution.get_or_none(student=user, task=task)
    if solution is not None:
        await solution.delete()

    await TaskSolution.create(
        content=content,
        extension=extension,
        student=user,
        task=task,
    )
