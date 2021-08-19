"""Модуль с хэндлерами главных страниц."""

from aiohttp import web
from aiohttp.web import Response, Request
import aiohttp_jinja2
from aiohttp_security import forget

from app import exceptions
from app.services import (
    get_user_courses,
    get_course_page_data,
    get_lesson_page_data,
    get_task_page_data,
    get_solution_page_data,
    get_waiting_solutions_page_data,
)
from app.utils import get_current_user, get_route


@aiohttp_jinja2.template("home.html")
async def index(request: Request) -> Response:
    """Главная страница."""
    user = await get_current_user(request)
    courses = await get_user_courses(user)
    return {"user": user, "courses": courses}


async def logout(request: Request) -> Response:
    """Выход из аккаунта."""
    redirect_response = web.HTTPFound("/")
    await forget(request, redirect_response)
    return redirect_response


@aiohttp_jinja2.template("profile.html")
async def profile(request: Request) -> Response:
    """Страница пользователя."""
    user = await get_current_user(request)
    if not user.is_authenticated:
        route = get_route(request, "register")
        return web.HTTPFound(location=route)
    return {"user": user}


@aiohttp_jinja2.template("search_courses.html")
async def search_courses(request: Request) -> Response:
    """Страница поиска публичных курсов."""
    user = await get_current_user(request)
    return {"user": user}


@aiohttp_jinja2.template("course.html")
async def course(request: Request) -> Response:
    """Страница курса."""
    try:
        user = await get_current_user(request)
        page_data = await get_course_page_data(request, user)
    except exceptions.CourseDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return page_data


@aiohttp_jinja2.template("lesson.html")
async def lesson(request: Request) -> Response:
    """Страница урока из курса."""
    try:
        user = await get_current_user(request)
        page_data = await get_lesson_page_data(request, user)
    except exceptions.LessonDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return page_data


@aiohttp_jinja2.template("task.html")
async def task(request: Request) -> Response:
    """Страница задачи из урока."""
    try:
        user = await get_current_user(request)
        page_data = await get_task_page_data(request, user)
    except exceptions.TaskDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return page_data


@aiohttp_jinja2.template("waiting_solutions.html")
async def waiting_solutions(request: Request) -> Response:
    """Страница ожидающих решений из данного курса."""
    try:
        user = await get_current_user(request)
        page_data = await get_waiting_solutions_page_data(request, user)
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return page_data


@aiohttp_jinja2.template("solution.html")
async def solution(request: Request) -> Response:
    """Страница решения задачи."""
    try:
        user = await get_current_user(request)
        page_data = await get_solution_page_data(request, user)
    except exceptions.SolutionDoesNotExist:
        raise web.HTTPNotFound()
    except exceptions.NotEnoughAccessRights:
        raise web.HTTPForbidden()
    else:
        return page_data
