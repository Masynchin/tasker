"""Модуль с функцией регистрации путей."""

from aiohttp.web import Application

from app import config
from app.views import ajax_handler
from app.views import form_handler
from app.views import token_handler
from app.views import site_handler


def setup_routes(app: Application):
    """Регистрация путей."""
    router = app.router

    router.add_get("/", site_handler.index, name="index")
    router.add_get("/profile", site_handler.profile, name="profile")
    router.add_get("/logout", site_handler.logout, name="logout")
    router.add_get(
        r"/course/{course_id:\d+}", site_handler.course, name="course"
    )
    router.add_get(
        "/search_courses", site_handler.search_courses, name="search_courses"
    )
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}",
        site_handler.lesson,
        name="lesson",
    )
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/task/{task_id:\d+}",
        site_handler.task,
        name="task",
    )
    router.add_get(
        r"/course/{course_id:\d+}/waiting_solutions",
        site_handler.waiting_solutions,
        name="waiting_solutions",
    )
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}"
        r"/task/{task_id:\d+}/solution/{solution_id:\d+}",
        site_handler.solution,
        name="solution",
    )

    router.add_get("/login", form_handler.login, name="login")
    router.add_post("/login", form_handler.handle_login)
    router.add_get("/register", form_handler.register, name="register")
    router.add_get(
        "/create_course",
        form_handler.handle_create_course,
        name="create_course",
    )
    router.add_post("/create_course", form_handler.handle_create_course)
    router.add_get(
        r"/course/{course_id:\d+}/create_lesson",
        form_handler.create_lesson_form,
        name="create_lesson",
    )
    router.add_post(
        r"/course/{course_id:\d+}/create_lesson",
        form_handler.handle_create_lesson,
    )
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task",
        form_handler.create_task_form,
        name="create_task",
    )
    router.add_post(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task",
        form_handler.handle_create_task,
    )
    router.add_get(
        "/activate_course_invite",
        form_handler.activate_course_invite,
        name="activate_course_invite",
    )

    router.add_post(
        r"/subscribe/{course_id:\d+}", ajax_handler.handle_course_subscribe
    )
    router.add_post(r"/search_courses", ajax_handler.handler_search_courses)
    router.add_post(
        r"/delete_course/{course_id:\d+}",
        ajax_handler.handle_delete_course,
        name="delete_course",
    )
    router.add_post(
        r"/submit_solution/{task_id:\d+}", ajax_handler.handle_task_solution
    )
    router.add_post("/mark_solution", ajax_handler.handle_delete_course)

    router.add_post(
        "/create_token_confirmation", token_handler.create_token_confirmation
    )
    router.add_get(
        r"/register/{token}",
        token_handler.handle_register_token,
        name="handle_register_token",
    )
    router.add_post(
        "/confirm_course_invite", token_handler.confirm_course_invite
    )

    router.add_static("/static/", path=config.STATIC_PATH, name="static")
