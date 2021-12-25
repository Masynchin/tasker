"""Модуль с хэндлерами путей курсов."""

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Response, Request

from app import exceptions
from app.services import (
    get_course_page_data,
    create_course,
    search_courses_by_title,
    on_course_subscribe_button_click,
    delete_course,
)
from app.utils import get_current_user, get_route


routes = web.RouteTableDef()


@routes.get(r"/course/{course_id:\d+}", name="course")
@aiohttp_jinja2.template("course.html")
async def course(request: Request) -> Response:
    """Страница курса."""
    course_id = request.match_info["course_id"]
    user = await get_current_user(request)

    try:
        page_data = await get_course_page_data(course_id, user)
    except exceptions.CourseDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return {"user": user, **page_data}


@routes.get("/create_course", name="create_course")
@aiohttp_jinja2.template("create_course.html")
async def create_course_form(request: Request) -> Response:
    """Создание курса."""
    user = await get_current_user(request)
    if not user.is_authenticated or not user.is_teacher:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    return {"user": user}


@routes.post("/create_course")
async def handle_create_course(request: Request) -> Response:
    """Обработка данных для создания курса."""
    solution_data = await request.post()
    user = await get_current_user(request)

    try:
        course = await create_course(solution_data, user)
    except exceptions.NotEnoughAccessRights:
        route = get_route(request, "create_course")
        return web.HTTPFound(location=route)
    else:
        route = get_route(request, "course", course_id=str(course.id))
        return web.HTTPFound(location=route)


@routes.get("/search_courses", name="search_courses")
@aiohttp_jinja2.template("search_courses.html")
async def search_courses(request: Request) -> Response:
    """Страница поиска публичных курсов."""
    user = await get_current_user(request)
    return {"user": user}


@routes.post("/search_courses")
async def handle_search_courses(request: Request) -> Response:
    """Обработка запроса поиска курса."""
    query = request.query.get("q", None)
    if query is None:
        return web.json_response({"error": "query param is missing"})

    courses = await search_courses_by_title(query)
    return web.json_response({"courses": courses})


@routes.post(r"/subscribe/{course_id:\d+}")
async def handle_course_subscribe(request: Request) -> Response:
    """Обработка запроса на запись в курс."""
    course_id = request.match_info["course_id"]
    user = await get_current_user(request)
    json_response = await on_course_subscribe_button_click(course_id, user)
    return web.json_response(json_response)


@routes.post(r"/delete_course/{course_id:\d+}", name="delete_course")
async def handle_delete_course(request: Request) -> Response:
    """Обработка запроса на удаление курса."""
    course_id = request.match_info["course_id"]
    user = await get_current_user(request)

    try:
        await delete_course(course_id, user)
    except exceptions.NotEnoughAccessRights:
        ...
    else:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)
