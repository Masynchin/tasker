"""Модуль с хэндлером главных страниц."""

from aiohttp import web
import aiohttp_jinja2
from aiohttp_security import forget

import exceptions
from services import (
    get_user_courses,
    get_course_page_data,
    get_lesson_page_data,
    get_task_page_data,
    get_solution_page_data,
    get_waiting_solutions_page_data,
)
from utils import get_current_user, get_route


class SiteHandler:
    """Обработчик главных страниц."""

    @aiohttp_jinja2.template("home.html")
    async def index(self, request):
        """Главная страница."""
        user = await get_current_user(request)
        courses = await get_user_courses(user)
        return {"user": user, "courses": courses}

    async def logout(self, request):
        """Выход из аккаунта."""
        redirect_response = web.HTTPFound("/")
        await forget(request, redirect_response)
        return redirect_response

    @aiohttp_jinja2.template("profile.html")
    async def profile(self, request):
        """Страница пользователя."""
        user = await get_current_user(request)
        if not user.is_authenticated:
            route = get_route(request, "register")
            return web.HTTPFound(location=route)
        return {"user": user}

    @aiohttp_jinja2.template("search_courses.html")
    async def search_courses(self, request):
        """Страница поиска публичных курсов."""
        user = await get_current_user(request)
        return {"user": user}

    @aiohttp_jinja2.template("course.html")
    async def course(self, request):
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
    async def lesson(self, request):
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
    async def task(self, request):
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
    async def waiting_solutions(self, request):
        """Страница ожидающих решений из данного курса."""
        try:
            user = await get_current_user(request)
            page_data = await get_waiting_solutions_page_data(request, user)
        except exceptions.NotEnoughAccessRights:
            raise web.HTTPForbidden()
        else:
            return page_data

    @aiohttp_jinja2.template("solution.html")
    async def solution(self, request):
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
