"""Сервис для работы с уроками."""

from typing import List, TypedDict

from tortoise.query_utils import Prefetch

from app import exceptions
from app.db.models import Course, Lesson, Task, TaskSolution, User
from app.db.models.task_solution import TaskSolutionStatus
from app.services.course_service import (
    get_course_by_id,
    is_course_teacher,
    raise_for_course_access,
)


class TaskData(TypedDict, total=False):
    """Модель данных задачи."""

    title: str
    task_id: int
    solution_status: TaskSolutionStatus


async def get_lesson_page_data(lesson_id: int, user: User) -> dict:
    """Получение данных для шаблона страницы курса в виде JSON."""
    lesson = await _get_lesson_by_id(lesson_id)
    await _raise_for_lesson_access(lesson, user)
    tasks = await _get_lesson_tasks(lesson, user)
    return {
        "lesson_id": lesson.id,
        "lesson_title": lesson.title,
        "tasks": tasks,
    }


async def _get_lesson_by_id(lesson_id: int) -> Lesson:
    """Получение урока по ID из запроса."""
    lesson = await Lesson.get_or_none(id=lesson_id)
    if lesson is None:
        raise exceptions.LessonDoesNotExist()

    return lesson


async def _raise_for_lesson_access(lesson: Lesson, user: User):
    """Выбрасываем ошибку, если курс закрытый и пользователь в нём нет."""
    course = await lesson.course
    await raise_for_course_access(course, user)


async def _get_lesson_tasks(lesson: Lesson, user: User) -> List[TaskData]:
    """Получение задач данного урока вместе с её решениями."""
    tasks = await _get_lesson_tasks_with_solutions(lesson, user)
    tasks_data = _convert_tasks_to_json_data(tasks)
    return tasks_data


async def _get_lesson_tasks_with_solutions(
    lesson: Lesson, user: User
) -> List[Task]:
    """Получение списка задач урока с их решением."""
    return await (
        Task.filter(lesson_id=lesson.id).prefetch_related(
            Prefetch(
                "solutions",
                queryset=TaskSolution.filter(student_id=user.id),
                to_attr="solution",
            )
        )
    )


def _convert_tasks_to_json_data(tasks: List[Task]) -> List[TaskData]:
    """Преобразование списка моделей Task в формат JSON."""
    tasks_data = []
    for task in tasks:
        task_data = {"title": task.title, "task_id": task.id}
        if task.solution:
            (solution,) = task.solution
            task_data["solution_status"] = solution.status
        tasks_data.append(task_data)

    return tasks_data


async def create_lesson(
    course_id: int, lesson_data: dict, user: User
) -> Lesson:
    """Создание нового урока в курсе."""
    course = await get_course_by_id(course_id)
    if not await is_course_teacher(course, user):
        raise exceptions.NotEnoughAccessRights()

    order_index = await _get_order_index(course)

    title = lesson_data["title"]
    lesson = await Lesson.create(
        title=title,
        order_index=order_index,
        course=course,
    )
    return lesson


async def _get_order_index(course: Course) -> int:
    """Получение порядкового номера для нового урока."""
    lessons = await course.lessons
    return len(lessons)
