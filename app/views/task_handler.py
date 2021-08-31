"""Модуль с хэндлерами путей задач."""

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Response, Request

from app import exceptions
from app.services import (
    get_task_page_data,
    get_course_by_id,
    is_course_teacher,
    create_task,
)
from app.utils import get_current_user, get_route


routes = web.RouteTableDef()


@routes.get(
    r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/task/{task_id:\d+}",
    name="task",
)
@aiohttp_jinja2.template("task.html")
async def task(request: Request) -> Response:
    """Страница задачи из урока."""
    try:
        task_id = request.match_info["task_id"]
        user = await get_current_user(request)
        page_data = await get_task_page_data(task_id, user)
    except exceptions.TaskDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        lesson_id = request.match_info["lesson_id"]
        course_id = request.match_info["course_id"]
        return {**page_data, "lesson_id": lesson_id, "course_id": course_id}


@routes.get(
    r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task",
    name="create_task",
)
@aiohttp_jinja2.template("create_task.html")
async def create_task_form(request: Request) -> Response:
    """Создание новой задачи в уроке."""
    user = await get_current_user(request)
    course_id = request.match_info["course_id"]
    course = await get_course_by_id(course_id)
    if not await is_course_teacher(course, user):
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    lesson_id = request.match_info["lesson_id"]
    return {"user": user, "course_id": course_id, "lesson_id": lesson_id}


@routes.post(r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task")
async def handle_create_task(request: Request) -> Response:
    """Обработка данных для создания новой задачи."""
    try:
        course_id = request.match_info["course_id"]
        lesson_id = request.match_info["lesson_id"]
        task_data = await request.post()
        user = await get_current_user(request)
        task = await create_task(course_id, lesson_id, task_data, user)
    except exceptions.NotEnoughAccessRights:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)
    else:
        route = get_route(
            request,
            "task",
            course_id=course_id,
            lesson_id=lesson_id,
            task_id=str(task.id),
        )
        return web.HTTPFound(location=route)
