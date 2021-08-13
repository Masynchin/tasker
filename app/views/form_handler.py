from aiohttp import web
import aiohttp_jinja2

import exceptions
from services import (
    login_user,
    register_user,
    is_course_teacher,
    create_course,
    create_lesson,
    create_task,
)
from utils import get_current_user, get_route


class FormHandler:
    """Обработчик форм и их заполнений"""

    @aiohttp_jinja2.template("register.html")
    async def register(self, request):
        """Страница регистрации"""
        user = await get_current_user(request)
        if user.is_authenticated:
            route = get_route(request, "index")
            return web.HTTPFound(location=route)

        return {"user": user}

    async def handle_register(self, request):
        """Обработка данных для регистрации"""
        try:
            redirect_response = web.HTTPFound("/")
            await register_user(request, redirect_response)
        except exceptions.NotUniqueEmail:
            route = get_route(request, "register")
            return web.HTTPFound(location=route)
        else:
            return redirect_response

    @aiohttp_jinja2.template("login.html")
    async def login(self, request):
        """Страница входа в аккаунт"""
        user = await get_current_user(request)
        if user.is_authenticated:
            route = get_route(request, "index")
            return web.HTTPFound(location=route)
        return {"user": user}

    async def handle_login(self, request):
        """Обработка данных для входа в аккаунт"""
        try:
            route = get_route(request, "index")
            redirect_response = web.HTTPFound(location=route)
            await login_user(request, redirect_response)
        except (exceptions.IncorrectPassword, exceptions.UserDoesNotExist):
            route = get_route(request, "login")
            return web.HTTPFound(location=route)
        else:
            return redirect_response

    @aiohttp_jinja2.template("create_course.html")
    async def create_course(self, request):
        """Создание курса"""
        user = await get_current_user(request)
        if not user.is_authenticated or not user.is_teacher:
            route = get_route(request, "index")
            return web.HTTPFound(location=route)

        return {"user": user}

    async def handle_create_course(self, request):
        """Обработка данных для создания курса"""
        try:
            user = await get_current_user(request)
            course = await create_course(request, user)
        except exceptions.NotEnoughAccessRights:
            route = get_route(request, "create_course")
            return web.HTTPFound(location=route)
        else:
            route = get_route(request, "course", course_id=str(course.id))
            return web.HTTPFound(location=route)

    @aiohttp_jinja2.template("create_lesson.html")
    async def create_lesson(self, request):
        """Создание нового урока в курсе"""
        user = await get_current_user(request)
        if not await is_course_teacher(request, user):
            route = get_route(request, "index")
            return web.HTTPFound(location=route)

        course_id = request.match_info["course_id"]
        return {"user": user, "course_id": course_id}

    async def handle_create_lesson(self, request):
        """Обработка данных для создания нового урока"""
        try:
            user = await get_current_user(request)
            lesson = await create_lesson(request, user)
        except exceptions.NotEnoughAccessRights:
            route = get_route(request, "create_course")
            return web.HTTPFound(location=route)
        else:
            course_id = request.match_info["course_id"]
            route = get_route(
                request,
                "lesson",
                course_id=course_id,
                lesson_id=str(lesson.id),
            )
            return web.HTTPFound(location=route)

    @aiohttp_jinja2.template("create_task.html")
    async def create_task(self, request):
        """Создание новой задачи в уроке"""
        user = await get_current_user(request)
        if not await is_course_teacher(request, user):
            route = get_route(request, "index")
            return web.HTTPFound(location=route)

        lesson_id = request.match_info["lesson_id"]
        course_id = request.match_info["course_id"]
        return {"user": user, "course_id": course_id, "lesson_id": lesson_id}

    async def handle_create_task(self, request):
        """Обработка данных для создания новой задачи"""
        try:
            user = await get_current_user(request)
            task = await create_task(request, user)
        except exceptions.NotEnoughAccessRights:
            route = get_route(request, "index")
            return web.HTTPFound(location=route)
        else:
            course_id = request.match_info["course_id"]
            lesson_id = request.match_info["lesson_id"]
            route = get_route(
                request,
                "task",
                course_id=course_id,
                lesson_id=lesson_id,
                task_id=str(task.id),
            )
            return web.HTTPFound(location=route)

    @aiohttp_jinja2.template("activate_course_invite.html")
    async def activate_course_invite(self, request):
        """Страница активации пригласительного токена"""
        user = await get_current_user(request)
        if not user.is_authenticated or user.is_teacher:
            route = get_route(request, "index")
            return web.HTTPFound(location=route)
        return {"user": user}
