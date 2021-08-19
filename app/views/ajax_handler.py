"""Модуль с хэндлерами AJAX-запросов."""

from aiohttp import web
from aiohttp.web import Response, Request

from app import exceptions
from app.services import (
    on_course_subscribe_button_click,
    search_courses_by_title,
    delete_course,
    handle_task_solution_request,
    mark_solution,
)
from app.utils import get_current_user, get_route


routes = web.RouteTableDef()


@routes.post(r"/subscribe/{course_id:\d+}")
async def handle_course_subscribe(request: Request) -> Response:
    """Обработка запроса на запись в курс."""
    user = await get_current_user(request)
    json_response = await on_course_subscribe_button_click(request, user)
    return web.json_response(json_response)


@routes.post("/search_courses")
async def handler_search_courses(request: Request) -> Response:
    """Обработка запроса поиска курса."""
    query = request.query.get("q", None)
    if query is None:
        return web.json_response({"error": "query param is missing"})
    courses = await search_courses_by_title(query)
    return web.json_response({"courses": courses})


@routes.post(r"/delete_course/{course_id:\d+}", name="delete_course")
async def handle_delete_course(request: Request) -> Response:
    """Обработка запроса на удаление курса."""
    try:
        user = await get_current_user(request)
        await delete_course(request, user)
    except exceptions.NotEnoughAccessRights:
        ...
    else:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)


@routes.post(r"/submit_solution/{task_id:\d+}")
async def handle_task_solution(request: Request) -> Response:
    """Обработка загрузки решения задачи."""
    try:
        task_id = request.match_info["task_id"]
        solution_data = await request.json()
        user = await get_current_user(request)
        await handle_task_solution_request(task_id, solution_data, user)
    except exceptions.TaskDoesNotExist:
        return web.json_response({"error": "task does not exist"})
    except exceptions.NotEnoughAccessRights:
        return web.json_response({"error": "not enough access rights"})
    else:
        return web.json_response({})


@routes.post("/mark_solution")
async def handle_mark_solution(request: Request) -> Response:
    """Обработка запроса оценивания решения."""
    user = await get_current_user(request)
    try:
        await mark_solution(request, user)
    except exceptions.NotEnoughAccessRights:
        return web.json_response({"error": "Не достаточно прав доступа"})
    else:
        return web.json_response({})
