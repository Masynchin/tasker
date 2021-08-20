"""Сервис для работы с решениями задач."""

from typing import Optional

from tortoise.query_utils import Q

from app import exceptions
from app.db.models import Course, TaskSolution, User
from app.db.models.task_solution import TaskSolutionStatus
from app.services.course_service import get_course_by_id
from tortoise.queryset import QuerySet


async def get_solution_page_data(solution_id: int, user: User) -> dict:
    """Получение данных для шаблона решения задачи в виде JSON."""
    solution = await _get_solution_by_id(solution_id)
    await _raise_for_solution_course_access(solution, user)
    solution_data = await _get_solution_data(solution)
    return {"user": user, "solution": solution_data}


async def _get_solution_by_id(solution_id: int) -> TaskSolution:
    """Получение решения задачи по его ID."""
    solution = await TaskSolution.get_or_none(id=solution_id)
    if solution is None:
        raise exceptions.SolutionDoesNotExist()

    return solution


async def _raise_for_solution_course_access(solution, user: User):
    """Выбрасываем ошибку, если пользователь не является учителем курса."""
    if not await _is_solution_task_teacher(solution, user):
        raise exceptions.NotEnoughAccessRights()


async def _is_solution_task_teacher(solution, user: User) -> bool:
    """Является ли пользователь учителем курса данного решения задачи."""
    teacher = await _get_solution_task_teacher(solution)
    return user == teacher


async def _get_solution_task_teacher(solution: TaskSolution) -> "User":
    """Получение учителя курса, в котором находится задача данного решения."""
    await solution.fetch_related("task")
    await solution.task.fetch_related("lesson")
    await solution.task.lesson.fetch_related("course")
    teacher = await solution.task.lesson.course.teacher
    return teacher


async def _get_solution_data(solution: TaskSolution) -> dict:
    solution_data_list = await (
        TaskSolution.filter(id=solution.id)
        .first()
        .values(
            task_title="task__title",
            task_condition="task__condition",
            student_name="student__username",
            solution_id="id",
            content="content",
        )
    )
    return solution_data_list[0]


async def mark_solution(mark_data: dict, user: User):
    """Обработка JSON-запроса при оценке решения."""
    solution_id = mark_data["solutionId"]
    solution = await _get_solution_by_id(solution_id)
    if not await _is_solution_task_teacher(solution, user):
        raise exceptions.NotEnoughAccessRights()

    is_correct = mark_data["isCorrect"]
    solution.set_status(is_correct)
    await solution.save()


async def get_waiting_solutions_page_data(course_id: int, user: User) -> dict:
    # точка в начале убирает ошибку D400
    """.
    Получение данных для шаблона страницы
    ожидающих решений данного курса в виде JSON.
    """
    course = await get_course_by_id(course_id)
    solutions = await _get_course_waiting_solutions(course)
    return {
        "user": user,
        "course": course,
        "solutions": solutions,
    }


async def _get_course_waiting_solutions(
    course: Course, sorted_by: Optional[str] = "timestamp"
) -> dict:
    """Получение всех ожидающих решений из данного курса в виде JSON."""
    base_query = _get_base_waiting_solutions_query(course)
    if sorted_by == "timestamp":
        query = base_query.order_by("timestamp")
    elif sorted_by == "student":
        query = base_query.order_by("student")
    elif sorted_by == "lesson":
        query = base_query.order_by("task__lesson")

    return await query.values(
        student_username="student__username",
        course_id="task__lesson__course_id",
        lesson_id="task__lesson_id",
        task_id="task_id",
        solution_id="id",
        task_title="task__title",
        timestamp="timestamp",
        content="content",
    )


def _get_base_waiting_solutions_query(
    course: Course,
) -> QuerySet[TaskSolution]:
    """Основа запроса на получение ожидающих решений."""
    return TaskSolution.filter(
        Q(task__lesson__course=course) & Q(status=TaskSolutionStatus.WAITING)
    )
