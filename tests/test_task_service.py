import pytest

from app import exceptions
from app.services import task_service


@pytest.mark.asyncio
async def test_create_task(create_user, create_course, create_lesson):
    teacher = await create_user(role="teacher")
    course = await create_course(teacher=teacher)
    lesson = await create_lesson(course=course, teacher=teacher)

    task_data = {
        "title": "title",
        "condition": "condition",
        "example": "example",
    }

    task = await task_service.create_task(
        course.id, lesson.id, task_data, teacher
    )

    assert task.title == task_data["title"]
    assert task.condition == task_data["condition"]
    assert task.example == task_data["example"]
    assert (await task.lesson) == lesson

    student = await create_user(role="student")
    with pytest.raises(exceptions.NotEnoughAccessRights):
        await task_service.create_task(
            course.id, lesson.id, task_data, student
        )


@pytest.mark.asyncio
async def test_get_task_by_id(create_task):
    task = await create_task()
    task_ = await task_service._get_task_by_id(task.id)
    assert task == task_

    with pytest.raises(exceptions.TaskDoesNotExist):
        await task_service._get_task_by_id(-1)


@pytest.mark.asyncio
async def test_raise_for_task_access(
    create_user, create_course, create_lesson, create_task
):
    teacher = await create_user(role="teacher")
    course = await create_course(teacher=teacher, is_private=True)
    lesson = await create_lesson(course=course, teacher=teacher)
    task = await create_task(course=course, lesson=lesson, teacher=teacher)

    await task_service._raise_for_task_access(task, teacher)

    student = await create_user(role="student")
    with pytest.raises(exceptions.NotEnoughAccessRights):
        await task_service._raise_for_task_access(task, student)
