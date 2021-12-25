"""Модуль с хэндлерами путей решений."""

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Response, Request

from app import exceptions
from app.services import (
    get_solution_page_data,
    get_waiting_solutions_page_data,
    create_or_update_solution,
    mark_solution,
)
from app.utils import get_current_user


routes = web.RouteTableDef()


@routes.get(
    r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}"
    r"/task/{task_id:\d+}/solution/{solution_id:\d+}",
    name="solution",
)
@aiohttp_jinja2.template("solution.html")
async def solution(request: Request) -> Response:
    """Страница решения задачи."""
    solution_id = request.match_info["solution_id"]
    user = await get_current_user(request)

    try:
        page_data = await get_solution_page_data(solution_id, user)
    except exceptions.SolutionDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return {"user": user, **page_data}


@routes.get(
    r"/course/{course_id:\d+}/waiting_solutions",
    name="waiting_solutions",
)
@aiohttp_jinja2.template("waiting_solutions.html")
async def waiting_solutions(request: Request) -> Response:
    """Страница ожидающих решений из данного курса."""
    course_id = request.match_info["course_id"]
    user = await get_current_user(request)

    try:
        page_data = await get_waiting_solutions_page_data(course_id, user)
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return {"user": user, **page_data}


@routes.post(r"/submit_solution/{task_id:\d+}")
async def handle_task_solution(request: Request) -> Response:
    """Обработка загрузки решения задачи."""
    task_id = request.match_info["task_id"]
    solution_data = await request.json()
    user = await get_current_user(request)

    try:
        await create_or_update_solution(task_id, solution_data, user)
    except exceptions.TaskDoesNotExist:
        return web.json_response({"error": "task does not exist"})
    except exceptions.NotEnoughAccessRights:
        return web.json_response({"error": "not enough access rights"})
    else:
        return web.json_response({})


@routes.post("/mark_solution")
async def handle_mark_solution(request: Request) -> Response:
    """Обработка запроса оценивания решения."""
    mark_data = await request.json()
    user = await get_current_user(mark_data)

    try:
        await mark_solution(request, user)
    except exceptions.NotEnoughAccessRights:
        return web.json_response({"error": "Не достаточно прав доступа"})
    else:
        return web.json_response({})
