"""Сервис для работы с курсами."""

from typing import Dict, List, Optional

from tortoise.functions import Count
from tortoise.queryset import QuerySet
from tortoise.query_utils import Q

from app import exceptions
from app.db.models import Course, Lesson, TaskSolution, User
from app.db.models.task_solution import TaskSolutionStatus
from app.services.token_service import create_course_invite_link


async def get_course_page_data(course_id: int, user: User) -> dict:
    """Получение данных для шаблона страницы курса в виде JSON."""
    course = await get_course_by_id(course_id)
    await raise_for_course_access(course, user)
    course_invite_link = create_course_invite_link(course.id)
    lessons = await get_course_lessons(course, user)
    is_subscribed = await check_is_user_subscribed(user, course)
    return {
        "user": user,
        "course": course,
        "lessons": lessons,
        "course_invite_link": course_invite_link,
        "is_subscribed": is_subscribed,
    }


async def get_course_lessons(course: Course, user: User) -> List[Lesson]:
    """Получение уроков данного курса."""
    return await (
        course.lessons.order_by("-order_index")
        .annotate(tasks_count=Count("tasks"))
        .annotate(
            correct_solutions_count=Count(
                "tasks__solutions",
                _filter=Q(
                    Q(tasks__solutions__student_id=user.id)
                    & Q(tasks__solutions__status=TaskSolutionStatus.CORRECT)
                ),
            )
        )
        .annotate(
            waiting_solutions_count=Count(
                "tasks__solutions",
                _filter=Q(
                    Q(tasks__solutions__student_id=user.id)
                    & Q(tasks__solutions__status=TaskSolutionStatus.WAITING)
                ),
            )
        )
    )


async def get_user_courses(user: User) -> List[Course]:
    """
    Получение курсов пользователя.
    Для ученика - проходимые, для учителя - созданные.
    """
    if not user.is_authenticated:
        courses = []
    elif user.is_student:
        courses = await _get_studied_courses(user)
    elif user.is_teacher:
        courses = await _get_taught_courses(user)
    return courses


async def _get_studied_courses(user: User) -> List[Course]:
    """Получение курсов, проходимых учеником."""
    return await user.studied_courses


async def _get_taught_courses(teacher: User) -> List[Course]:
    """Получение курсов, преподоваемых учителем."""
    return await teacher.taught_courses


async def create_course(course_data: dict, user: User) -> Course:
    """Создание нового курса."""
    if not user.is_authenticated or not user.is_teacher:
        raise exceptions.NotEnoughAccessRights()

    title = course_data["title"]
    description = course_data["description"]
    is_private = "isPrivate" in course_data
    course = await Course.create(
        title=title,
        description=description,
        is_private=is_private,
        teacher=user,
    )
    return course


async def get_course_by_id(course_id: int) -> Course:
    """Получение курса по его ID."""
    course = await Course.get_or_none(id=course_id)
    if course is None:
        raise exceptions.CourseDoesNotExist()

    return course


async def raise_for_course_access(course: Course, user: User):
    """Выбрасываем ошибку, если курс закрытый и пользователя в нём нет."""
    if course.is_private:
        await course.fetch_related("teacher", "students")
        if user != course.teacher and user not in course.students:
            raise exceptions.NotEnoughAccessRights()


async def on_course_subscribe_button_click(
    course_id: int, user: User
) -> Dict[str, bool]:
    """Запись пользователя на курс; отпись, если уже подписан.

    Функция возвращает JSON формата -
    {
        "isSubscribed": bool  # подписан ли пользователь на курс
                              # после выполнения функции
    }.
    """
    course = await get_course_by_id(course_id)
    await subscribe_or_unsubscribe_user_to_course(user, course)
    is_subscribed = await check_is_user_subscribed(user, course)
    return {"isSubscribed": is_subscribed}


async def subscribe_or_unsubscribe_user_to_course(user: User, course: Course):
    """
    Подписка пользователя на курс, если не записан.
    Отписка пользователя от курса, если уже записан.
    """
    is_subscribed = await check_is_user_subscribed(user, course)
    if is_subscribed:
        await course.students.remove(user)
    else:
        await course.students.add(user)


async def subscribe_user_to_course_if_not_subscribed(
    user: User, course: Course
):
    """Подписка пользователя, если не подписан на курс."""
    is_subscribed = await check_is_user_subscribed(user, course)
    if not is_subscribed:
        await course.students.add(user)


async def check_is_user_subscribed(user: User, course: Course) -> bool:
    """Подписан ли пользователь на данный курс."""
    students = await course.students
    return user in students


async def search_courses_by_title(title_query: str) -> List[dict]:
    """Поиск курсов по их названию."""
    courses = await (
        Course.filter(
            Q(is_private=False) & Q(title__icontains=title_query)
        ).values("id", "title", "description")
    )
    return courses


async def delete_course(course_id: int, user: User):
    """Удаление курса."""
    course = await get_course_by_id(course_id)
    if not await is_course_teacher(course, user):
        raise exceptions.NotEnoughAccessRights()

    await course.delete()


async def is_course_teacher(course: Course, user: User) -> bool:
    """Является ли пользователь учителем в курсе."""
    teacher = await course.teacher
    return user == teacher


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
