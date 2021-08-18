"""Сервис для работы с решениями задач."""

from aiohttp.web_request import Request

from app import exceptions
from app.db.models import TaskSolution, User


async def get_solution_page_data(request: Request, user: User) -> dict:
    """Получение данных для шаблона решения задачи в виде JSON."""
    solution = await _get_solution_from_request(request)
    await _raise_for_solution_course_access(solution, user)
    solution_data = await _get_solution_data(solution)
    return {"user": user, "solution": solution_data}


async def _get_solution_from_request(request: Request) -> TaskSolution:
    """Получение решения задачи из запроса."""
    solution_id = request.match_info["solution_id"]
    solution = await _get_solution_by_id(solution_id)
    return solution


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


async def mark_solution(request: Request, user: User):
    """Обработка JSON-запроса при оценке решения."""
    data = await request.json()
    solution_id = data["solutionId"]
    solution = await _get_solution_by_id(solution_id)
    if not await _is_solution_task_teacher(solution, user):
        raise exceptions.NotEnoughAccessRights()

    is_correct = data["isCorrect"]
    solution.set_status(is_correct)
    await solution.save()
