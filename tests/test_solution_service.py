import pytest

from app import exceptions
from app.services import solution_service
from app.services.course_service import (
    subscribe_user_to_course,
)


@pytest.mark.asyncio
async def test_create_or_update_solution(
    create_teacher, create_student, create_course, create_lesson, create_task
):
    teacher = await create_teacher()
    student = await create_student()
    course = await create_course(teacher=teacher)
    await subscribe_user_to_course(student, course)

    lesson = await create_lesson(course=course, teacher=teacher)
    task = await create_task(course=course, lesson=lesson, teacher=teacher)

    solution_data = {
        "content": "content",
        "extension": "ext",
    }
    solution = await solution_service.create_or_update_solution(
        task.id, solution_data, student
    )

    assert solution.content == solution_data["content"]
    assert solution.extension == solution_data["extension"]
    assert (await solution.student) == student
    assert (await solution.task) == task

    with pytest.raises(exceptions.NotEnoughAccessRights):
        await solution_service.create_or_update_solution(
            task.id, solution_data, teacher
        )


@pytest.mark.asyncio
async def test_get_solution_by_id(create_solution):
    solution = await create_solution()
    solution_ = await solution_service._get_solution_by_id(solution.id)
    assert solution == solution_

    with pytest.raises(exceptions.SolutionDoesNotExist):
        await solution_service._get_solution_by_id(-1)


@pytest.mark.asyncio
async def test_get_solution_task_teacher(
    create_teacher,
    create_student,
    create_course,
    create_lesson,
    create_task,
    create_solution,
):
    teacher = await create_teacher()
    student = await create_student()
    course = await create_course(teacher=teacher)
    await subscribe_user_to_course(student, course)

    lesson = await create_lesson(course=course, teacher=teacher)
    task = await create_task(course=course, lesson=lesson, teacher=teacher)
    solution = await create_solution(task=task, student=student)

    teacher_ = await solution_service._get_solution_task_teacher(solution)
    assert teacher == teacher_
