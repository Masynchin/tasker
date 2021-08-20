import pytest

from app import exceptions
from app.services import lesson_service
from app.services.course_service import (
    subscribe_user_to_course_if_not_subscribed,
)


@pytest.mark.asyncio
async def test_create_lesson(create_user, create_course):
    student = await create_user(role="student")
    teacher = await create_user(role="teacher")
    course = await create_course(teacher=teacher)

    with pytest.raises(exceptions.NotEnoughAccessRights):
        await lesson_service.create_lesson(course.id, {}, student)

    lesson_data = {"title": "title"}
    lesson = await lesson_service.create_lesson(
        course.id, lesson_data, teacher
    )
    assert lesson.title == lesson_data["title"]
    assert (await lesson.course) == course


@pytest.mark.asyncio
async def test_get_lesson_by_id(create_lesson):
    lesson = await create_lesson()
    lesson_ = await lesson_service._get_lesson_by_id(lesson.id)
    assert lesson == lesson_

    with pytest.raises(exceptions.LessonDoesNotExist):
        await lesson_service._get_lesson_by_id(-1)


@pytest.mark.asyncio
async def test_raise_for_lesson_access(
    create_user, create_course, create_lesson
):
    teacher = await create_user(role="teacher")
    course = await create_course(teacher=teacher, is_private=True)

    lesson = await create_lesson(course=course, teacher=teacher)

    student = await create_user(role="student")
    with pytest.raises(exceptions.NotEnoughAccessRights):
        await lesson_service._raise_for_lesson_access(lesson, student)

    await subscribe_user_to_course_if_not_subscribed(student, course)
    await lesson_service._raise_for_lesson_access(lesson, student)
