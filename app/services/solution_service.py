from db.models import TaskSolution
from db.models.task_solution import TaskSolutionStatus
from exceptions import SolutionDoesNotExist, NotEnoughAccessRights


async def get_solution_page_data(request, user):
    """Получение данных для шаблона решения задачи в виде JSON"""
    solution = await _get_solution_from_request(request)
    await _raise_for_access(solution, user)
    solution_data = await _get_solution_data(solution)
    return {"user": user, "solution": solution_data}


async def _get_solution_from_request(request):
    """Получение решения задачи из запроса"""
    solution_id = request.match_info["solution_id"]
    solution = await _get_solution_by_id(solution_id)
    return solution


async def _get_solution_by_id(solution_id):
    """Получение решения задачи по его ID"""
    solution = await TaskSolution.get_or_none(id=solution_id)
    if solution is None:
        raise SolutionDoesNotExist()
    return solution


async def _raise_for_access(solution, user):
    """Выбрасываем ошибку, если пользователь не является учителем курса"""
    if not await _is_solution_task_teacher(solution, user):
        raise NotEnoughAccessRights()


async def _is_solution_task_teacher(solution, user):
    """Является ли пользователь учителем курса данного решения задачи"""
    teacher = await _get_solution_task_teacher(solution)
    return user == teacher


async def _get_solution_task_teacher(solution):
    """Получение учителя курса, в котором находится задача данного решения"""
    await solution.fetch_related("task")
    await solution.task.fetch_related("lesson")
    await solution.task.lesson.fetch_related("course")
    teacher = await solution.task.lesson.course.teacher
    return teacher


async def _get_solution_data(solution):
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


async def mark_solution(request, user):
    """Обработка JSON-запроса при оценке решения"""
    data = await request.json()
    solution_id = data["solutionId"]
    solution = await _get_solution_by_id(solution_id)
    if not await _is_solution_task_teacher(solution, user):
        raise NotEnoughAccessRights()

    is_correct = data["isCorrect"]
    if is_correct:
        solution.status = TaskSolutionStatus.CORRECT
    else:
        solution.status = TaskSolutionStatus.INCORRECT
    await solution.save()
