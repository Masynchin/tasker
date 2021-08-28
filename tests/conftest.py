import pytest

from app.db import init_test_db, close_test_db
from app.services import course_service
from app.services import lesson_service
from app.services import solution_service
from app.services import task_service
from app.services import user_service


@pytest.fixture(autouse=True)
async def open_test_db():
    await init_test_db()
    yield
    await close_test_db()


@pytest.fixture
def unique_email():
    prefix = "a"

    def _unique_email():
        nonlocal prefix
        prefix = chr(ord(prefix) + 1)
        return f"{prefix}@mail.com"

    return _unique_email


@pytest.fixture
def create_user(unique_email):
    async def _create_user(
        email=None, username=None, password=None, role=None
    ):
        user_data = {
            "email": email or unique_email(),
            "username": username or "username",
            "password": password or "12345678",
            "role": role or "student",
        }
        return await user_service.create_user(user_data)

    return _create_user


@pytest.fixture
def create_teacher(create_user):
    async def _create_teacher(**kwargs):
        return await create_user(**kwargs, role="teacher")

    return _create_teacher


@pytest.fixture
def create_student(create_user):
    async def _create_student(**kwargs):
        return await create_user(**kwargs, role="student")

    return _create_student


@pytest.fixture
def create_course(create_teacher):
    async def _create_course(
        title=None, description=None, is_private=False, teacher=None
    ):
        course_data = {
            "title": title or "title",
            "description": description or "description",
        }
        if is_private:
            course_data["isPrivate"] = True

        teacher = teacher or (await create_teacher())
        return await course_service.create_course(course_data, teacher)

    return _create_course


@pytest.fixture
def create_lesson(create_teacher, create_course):
    async def _create_lesson(title=None, course=None, teacher=None):
        lesson_data = {
            "title": title or "title",
        }
        if course is None or teacher is None:
            teacher = await create_teacher()
            course = await create_course(teacher=teacher)

        return await lesson_service.create_lesson(
            course.id, lesson_data, teacher
        )

    return _create_lesson


@pytest.fixture
def create_task(create_teacher, create_course, create_lesson):
    async def _create_task(
        title=None,
        condition=None,
        example=None,
        course=None,
        lesson=None,
        teacher=None,
    ):
        task_data = {
            "title": title or "title",
            "condition": condition or "condition",
            "example": example or "example",
        }

        if None in {course, lesson, teacher}:
            teacher = await create_teacher()
            course = await create_course(teacher=teacher)
            lesson = await create_lesson(course=course, teacher=teacher)

        return await task_service.create_task(
            course.id, lesson.id, task_data, teacher
        )

    return _create_task


@pytest.fixture
def create_solution(
    create_teacher, create_student, create_course, create_lesson, create_task
):
    async def _create_solution(
        content=None, extension=None, task=None, student=None
    ):
        solution_data = {
            "content": content or "content",
            "extension": extension or "ext",
        }
        if None in {task, student}:
            teacher = await create_teacher()
            course = await create_course(teacher=teacher)
            lesson = await create_lesson(course=course, teacher=teacher)
            task = await create_task(
                course=course, lesson=lesson, teacher=teacher
            )
            student = await create_student()
            await course_service.subscribe_user_to_course(student, course)

        solution = await solution_service.create_or_update_solution(
            task.id, solution_data, student
        )
        return solution

    return _create_solution
