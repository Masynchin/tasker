from tortoise.functions import Count
from tortoise.query_utils import Q

from db.models import Course, TaskSolution
from db.models.task_solution import TaskSolutionStatus
from exceptions import NotEnoughAccessRights, CourseDoesNotExist
from services.token_service import create_course_invite_link


async def get_course_page_data(request, user):
    """Получение данных для шаблона страницы курса в виде JSON"""
    course = await get_course_from_request(request)
    await _raise_for_access(course, user)
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


async def get_course_lessons(course, user):
    """Получение уроков данного курса"""
    return await (
        course.lessons
        .order_by("-order_index")
        .annotate(tasks_count=Count("tasks"))
        .annotate(
            correct_solutions_count=Count(
                "tasks__solutions",
                _filter=Q(
                    Q(tasks__solutions__student_id=user.id) &
                    Q(tasks__solutions__status=TaskSolutionStatus.CORRECT)
                )
            )
        )
        .annotate(
            waiting_solutions_count=Count(
                "tasks__solutions",
                _filter=Q(
                    Q(tasks__solutions__student_id=user.id) &
                    Q(tasks__solutions__status=TaskSolutionStatus.WAITING)
                )
            )
        )
    )


async def get_user_courses(user):
    """
    Получение курсов пользователя.
    Для ученика - проходимые, для учителя - созданные
    """
    if not user.is_authenticated:
        courses = []
    elif user.is_student:
        courses = await _get_studied_courses(user)
    elif user.is_teacher:
        courses = await _get_taught_courses(user)
    return courses


async def _get_studied_courses(user):
    """Получение курсов, проходимых учеником"""
    return await user.studied_courses


async def _get_taught_courses(teacher):
    """Получение курсов, преподоваемых учителем"""
    return await teacher.taught_courses


async def create_course(request, user):
    """Создание нового курса"""
    if not user.is_authenticated or not user.is_teacher:
        raise NotEnoughAccessRights()

    data = await request.post()
    title = data["title"]
    description = data["description"]
    is_private = "isPrivate" in data
    course = await Course.create(
        title=title,
        description=description,
        is_private=is_private,
        teacher=user,
    )
    return course


async def get_course_from_request(request):
    """Получение курса по ID из запроса"""
    course_id = request.match_info["course_id"]
    return await get_course_by_id(course_id)


async def get_course_by_id(course_id):
    """Получение курса по его ID"""
    course = await Course.get_or_none(id=course_id)
    if course is None:
        raise CourseDoesNotExist()
    return course


async def _raise_for_access(course, user):
    """Выбрасываем ошибку, если курс закрытый и пользователь в нём нет"""
    if course.is_private:
        teacher = await course.teacher
        course_students = await course.students
        if user != teacher and user not in course_students:
            raise NotEnoughAccessRights()


async def on_course_subscribe_button_click(request, user):
    """Запись пользователя на курс; отпись, если уже подписан.

    Функция возвращает JSON формата -
    {
        "isSubscribed": bool  # подписан ли пользователь на курс
                              # после выполнения функции
    }
    """
    course = await get_course_from_request(request)
    await subscribe_or_unsubscribe_user_to_course(user, course)
    is_subscribed = await check_is_user_subscribed(user, course)
    return {"isSubscribed": is_subscribed}


async def subscribe_or_unsubscribe_user_to_course(user, course):
    """
    Подписка пользователя на курс, если не записан.
    Отписка пользователя от курса, если уже записан
    """
    is_subscribed = await check_is_user_subscribed(user, course)
    if is_subscribed:
        await course.students.remove(user)
    else:
        await course.students.add(user)


async def subscribe_user_to_course_if_not_subscribed(user, course):
    """Подписка пользователя, если не подписан на курс"""
    is_subscribed = await check_is_user_subscribed(user, course)
    if not is_subscribed:
        await course.students.add(user)


async def check_is_user_subscribed(user, course):
    """Подписан ли пользователь на данный курс"""
    students = await course.students
    return user in students


async def search_courses_by_title(query):
    """Поиск курсов по их названию"""
    courses = await (
        Course
        .filter(Q(is_private=False) & Q(title__icontains=query))
        .values("id", "title", "description")
    )
    return courses


async def delete_course(request, user):
    """Удаление курса"""
    if not await is_course_teacher(request, user):
        raise NotEnoughAccessRights()
    course = await get_course_from_request(request)
    await course.delete()


async def is_course_teacher(request, user):
    """Является ли пользователь учителем в курсе"""
    course = await get_course_from_request(request)
    teacher = await course.teacher
    return user == teacher


async def get_waiting_solutions_page_data(request, user):
    """
    Получение данных для шаблона страницы
    ожидающих решений данного курса в виде JSON
    """
    course = await get_course_from_request(request)
    solutions = await _get_course_waiting_solutions(course)
    return {
        "user": user,
        "course": course,
        "solutions": solutions,
    }


async def _get_course_waiting_solutions(course, sorted_by="timestamp"):
    """Получение всех ожидающих решений из данного курса в виде JSON"""
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


def _get_base_waiting_solutions_query(course):
    """Основа запроса на получение ожидающих решений"""
    return TaskSolution.filter(
        Q(task__lesson__course=course) &
        Q(status=TaskSolutionStatus.WAITING)
    )
