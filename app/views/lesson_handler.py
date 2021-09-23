"""Модуль с хэндлерами путей уроков."""

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Response, Request

from app import exceptions
from app.services import (
    get_course_by_id,
    is_course_teacher,
    create_lesson,
    get_lesson_page_data,
)
from app.utils import get_current_user, get_route


routes = web.RouteTableDef()


@routes.get(r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}", name="lesson")
@aiohttp_jinja2.template("lesson.html")
async def lesson(request: Request) -> Response:
    """Страница урока из курса."""
    try:
        lesson_id = request.match_info["lesson_id"]
        user = await get_current_user(request)
        page_data = await get_lesson_page_data(lesson_id, user)
    except exceptions.LessonDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        course_id = request.match_info["course_id"]
        return {"user": user, "course_id": course_id, **page_data}


@routes.get(r"/course/{course_id:\d+}/create_lesson", name="create_lesson")
@aiohttp_jinja2.template("create_lesson.html")
async def create_lesson_form(request: Request) -> Response:
    """Создание нового урока в курсе."""
    user = await get_current_user(request)
    course_id = request.match_info["course_id"]
    course = await get_course_by_id(course_id)
    if not await is_course_teacher(course, user):
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    return {"user": user, "course_id": course_id}


@routes.post(r"/course/{course_id:\d+}/create_lesson")
async def handle_create_lesson(request: Request) -> Response:
    """Обработка данных для создания нового урока."""
    try:
        course_id = request.match_info["course_id"]
        lesson_data = await request.post()
        user = await get_current_user(request)
        lesson = await create_lesson(course_id, lesson_data, user)
    except exceptions.NotEnoughAccessRights:
        route = get_route(request, "create_course")
        return web.HTTPFound(location=route)
    else:
        route = get_route(
            request,
            "lesson",
            course_id=course_id,
            lesson_id=str(lesson.id),
        )
        return web.HTTPFound(location=route)
