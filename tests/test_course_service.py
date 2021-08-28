import pytest

from app import exceptions
from app.db.models.user import AnonimousUser
from app.services import course_service


@pytest.mark.asyncio
async def test_create_private_course(create_user):
    user = await create_user(role="teacher")

    course_data = {
        "title": "Course title",
        "description": "Course desctiption",
        "isPrivate": True,
    }
    course = await course_service.create_course(course_data, user)
    assert course.title == course_data["title"]
    assert course.description == course_data["description"]
    assert course.is_private


@pytest.mark.asyncio
async def test_public_create_course(create_user):
    user = await create_user(role="teacher")

    course_data = {
        "title": "Course title",
        "description": "Course desctiption",
    }
    course = await course_service.create_course(course_data, user)
    assert course.title == course_data["title"]
    assert course.description == course_data["description"]
    assert not course.is_private


@pytest.mark.asyncio
async def test_invalid_user_create_course(create_user):
    user = await create_user(role="student")
    with pytest.raises(exceptions.NotEnoughAccessRights):
        await course_service.create_course({}, user)

    user = AnonimousUser()
    with pytest.raises(exceptions.NotEnoughAccessRights):
        await course_service.create_course({}, user)


@pytest.mark.asyncio
async def test_get_course_by_id(create_course):
    course = await create_course()
    course_id = course.id
    course_ = await course_service.get_course_by_id(course_id)
    assert course == course_

    with pytest.raises(exceptions.CourseDoesNotExist):
        await course_service.get_course_by_id(course_id=-1)


@pytest.mark.asyncio
async def test_delete_course(create_user, create_course):
    teacher = await create_user(role="teacher")
    course = await create_course(teacher=teacher)
    course_id = course.id

    await course_service.delete_course(course_id, teacher)

    user = await create_user(role="student")
    course = await create_course(teacher=teacher)
    with pytest.raises(exceptions.NotEnoughAccessRights):
        await course_service.delete_course(course.id, user)


@pytest.mark.asyncio
async def test_is_course_teacher(create_user, create_course):
    teacher = await create_user(role="teacher")
    course = await create_course(teacher=teacher)

    assert await course_service.is_course_teacher(course, teacher)

    another_teacher = await create_user(role="teacher")
    assert not await course_service.is_course_teacher(course, another_teacher)

    student = await create_user(role="teacher")
    assert not await course_service.is_course_teacher(course, student)

    anonimous = AnonimousUser()
    assert not await course_service.is_course_teacher(course, anonimous)


@pytest.mark.asyncio
async def test_check_is_user_subscribed(create_user, create_course):
    student = await create_user(role="student")
    course = await create_course()

    assert not await course_service.check_is_user_subscribed(student, course)

    await course_service.subscribe_user_to_course(student, course)
    assert await course_service.check_is_user_subscribed(student, course)


@pytest.mark.asyncio
async def test_subscribe_user_to_course(create_user, create_course):
    student = await create_user(role="student")
    course = await create_course()
    assert not await course_service.check_is_user_subscribed(student, course)

    await course_service.subscribe_user_to_course(student, course)
    assert await course_service.check_is_user_subscribed(student, course)


@pytest.mark.asyncio
async def test_subscribe_or_unsubscribe_user_to_course(
    create_user, create_course
):
    student = await create_user(role="student")
    course = await create_course()
    assert not await course_service.check_is_user_subscribed(student, course)

    is_subscribed = (
        await course_service.subscribe_or_unsubscribe_user_to_course(
            student, course
        )
    )
    assert is_subscribed

    is_subscribed = (
        await course_service.subscribe_or_unsubscribe_user_to_course(
            student, course
        )
    )
    assert not is_subscribed


@pytest.mark.asyncio
async def test_get_user_courses(create_user, create_course):
    anonimous = AnonimousUser()
    assert not await course_service.get_user_courses(anonimous)

    teacher = await create_user(role="teacher")
    assert not await course_service.get_user_courses(teacher)

    course = await create_course(teacher=teacher)
    taught_courses = await course_service.get_user_courses(teacher)
    assert len(taught_courses) == 1
    assert course in taught_courses

    student = await create_user(role="student")
    assert not await course_service.get_user_courses(student)

    await course_service.subscribe_user_to_course(student, course)
    studied_courses = await course_service.get_user_courses(student)
    assert len(studied_courses) == 1
    assert course in studied_courses


@pytest.mark.asyncio
async def test_raise_for_course_access(create_user, create_course):
    public_course = await create_course(is_private=False)

    anonimous = AnonimousUser()
    student = await create_user(role="student")
    teacher = await create_user(role="teacher")

    for user in (anonimous, student, teacher):
        await course_service.raise_for_course_access(public_course, user)

    private_teacher = await create_user(role="teacher")
    private_course = await create_course(
        is_private=True, teacher=private_teacher
    )
    private_student = await create_user(role="student")
    await course_service.subscribe_user_to_course(
        private_student, private_course
    )

    for user in (anonimous, student, teacher):
        with pytest.raises(exceptions.NotEnoughAccessRights):
            await course_service.raise_for_course_access(private_course, user)

    for private_user in (private_student, private_teacher):
        await course_service.raise_for_course_access(
            private_course, private_user
        )


@pytest.mark.asyncio
async def test_search_courses_by_title(create_course):
    correct_titles = {"max", "maximum", "Course by Max", "Reb-black xamax"}
    incorrect_titles = {"min", "ma-x", "ma x", "мах"}

    for title in (*correct_titles, *incorrect_titles):
        await create_course(title=title)

    courses = await course_service.search_courses_by_title("max")
    courses_titles = {course["title"] for course in courses}

    assert courses_titles == correct_titles
    assert not (courses_titles & incorrect_titles)


@pytest.mark.asyncio
async def test_on_course_subscribe_button_click(create_user, create_course):
    student = await create_user()
    course = await create_course()

    response = await course_service.on_course_subscribe_button_click(
        course.id, student
    )
    assert response["isSubscribed"]

    response = await course_service.on_course_subscribe_button_click(
        course.id, student
    )
    assert not response["isSubscribed"]
