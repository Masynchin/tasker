from tortoise.query_utils import Prefetch

from db.models import Lesson, Task, TaskSolution
from exceptions import NotEnoughAccessRights, LessonDoesNotExist
from services.course_service import (
    get_course_from_request,
    is_course_teacher,
    raise_for_course_access,
)


async def get_lesson_page_data(request, user):
    """Получение данных для шаблона страницы курса в виде JSON"""
    lesson = await get_lesson_from_request(request)
    await _raise_for_lesson_access(lesson, user)
    tasks = await _get_lesson_tasks(lesson, user)
    course_id = request.match_info["course_id"]
    return {
        "user": user,
        "course_id": course_id,
        "lesson_id": lesson.id,
        "lesson_title": lesson.title,
        "tasks": tasks,
    }


async def get_lesson_from_request(request):
    """Получение урока из запроса"""
    lesson_id = request.match_info["lesson_id"]
    lesson = await _get_lesson_by_id(lesson_id)
    return lesson


async def _get_lesson_by_id(lesson_id):
    """Получение урока по ID из запроса"""
    lesson = await Lesson.get_or_none(id=lesson_id)
    if lesson is None:
        raise LessonDoesNotExist()
    return lesson


async def _raise_for_lesson_access(lesson, user):
    """Выбрасываем ошибку, если курс закрытый и пользователь в нём нет"""
    course = await lesson.course
    await raise_for_course_access(course, user)


async def _get_lesson_tasks(lesson, user):
    """Получение задач данного урока вместе с её решениями"""
    tasks = await _get_lesson_tasks_with_solutions(lesson, user)
    tasks_data = _convert_tasks_to_json_data(tasks)
    return tasks_data


async def _get_lesson_tasks_with_solutions(lesson, user):
    """Получение списка задач урока с их решением"""
    return await (
        Task
        .filter(lesson_id=lesson.id)
        .prefetch_related(
            Prefetch(
                "solutions",
                queryset=TaskSolution.filter(student_id=user.id),
                to_attr="solution",
            )
        )
    )


def _convert_tasks_to_json_data(tasks):
    """Преобразование списка моделей Task в формат JSON"""
    tasks_data = []
    for task in tasks:
        task_data = {"title": task.title, "task_id": task.id}
        if task.solution:
            solution, = task.solution
            task_data["solution_status"] = solution.status
        tasks_data.append(task_data)

    return tasks_data


async def create_lesson(request, user):
    """Создание нового урока в курсе"""
    if not await is_course_teacher(request, user):
        raise NotEnoughAccessRights()

    course = await get_course_from_request(request)
    order_index = await _get_order_index(course)

    data = await request.post()
    title = data["title"]
    lesson = await Lesson.create(
        title=title,
        order_index=order_index,
        course=course,
    )
    return lesson


async def _get_order_index(course):
    """Получение порядкового номера для нового урока"""
    lessons = await course.lessons
    return len(lessons)
