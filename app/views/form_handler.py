"""Модуль с хэндлерами форм."""

from aiohttp import web
from aiohttp.web import Response, Request
import aiohttp_jinja2
from aiohttp_security import remember

from app import exceptions
from app.services import (
    get_user,
    is_course_teacher,
    create_course,
    create_lesson,
    create_task,
)
from app.utils import get_current_user, get_route


routes = web.RouteTableDef()


@routes.get("/register", name="register")
@aiohttp_jinja2.template("register.html")
async def register(request: Request) -> Response:
    """Страница регистрации."""
    user = await get_current_user(request)
    if user.is_authenticated:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    return {"user": user}


@routes.get("/login", name="login")
@aiohttp_jinja2.template("login.html")
async def login(request: Request) -> Response:
    """Страница входа в аккаунт."""
    user = await get_current_user(request)
    if user.is_authenticated:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)
    return {"user": user}


@routes.post("/login")
async def handle_login(request: Request) -> Response:
    """Обработка данных для входа в аккаунт."""
    try:
        route = get_route(request, "index")
        user = await get_user(request)
    except (exceptions.IncorrectPassword, exceptions.UserDoesNotExist):
        route = get_route(request, "login")
        return web.HTTPFound(location=route)
    else:
        redirect_response = web.HTTPFound(location=route)
        await remember(request, redirect_response, str(user.id))
        return redirect_response


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
    try:
        user = await get_current_user(request)
        course = await create_course(request, user)
    except exceptions.NotEnoughAccessRights:
        route = get_route(request, "create_course")
        return web.HTTPFound(location=route)
    else:
        route = get_route(request, "course", course_id=str(course.id))
        return web.HTTPFound(location=route)


@routes.get(r"/course/{course_id:\d+}/create_lesson", name="create_lesson")
@aiohttp_jinja2.template("create_lesson.html")
async def create_lesson_form(request: Request) -> Response:
    """Создание нового урока в курсе."""
    user = await get_current_user(request)
    if not await is_course_teacher(request, user):
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    course_id = request.match_info["course_id"]
    return {"user": user, "course_id": course_id}


@routes.post(r"/course/{course_id:\d+}/create_lesson")
async def handle_create_lesson(request: Request) -> Response:
    """Обработка данных для создания нового урока."""
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


@routes.get(
    r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task",
    name="create_task",
)
@aiohttp_jinja2.template("create_task.html")
async def create_task_form(request: Request) -> Response:
    """Создание новой задачи в уроке."""
    user = await get_current_user(request)
    if not await is_course_teacher(request, user):
        route = get_route(request, "index")
        return web.HTTPFound(location=route)

    lesson_id = request.match_info["lesson_id"]
    course_id = request.match_info["course_id"]
    return {"user": user, "course_id": course_id, "lesson_id": lesson_id}


@routes.post(r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task")
async def handle_create_task(request: Request) -> Response:
    """Обработка данных для создания новой задачи."""
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


@routes.get("/activate_course_invite", name="activate_course_invite")
@aiohttp_jinja2.template("activate_course_invite.html")
async def activate_course_invite(request: Request) -> Response:
    """Страница активации пригласительного токена."""
    user = await get_current_user(request)
    if not user.is_authenticated or user.is_teacher:
        route = get_route(request, "index")
        return web.HTTPFound(location=route)
    return {"user": user}
