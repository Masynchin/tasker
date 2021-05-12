import config


def setup_routes(app, site_handler, form_handler, ajax_handler, token_handler):
    """Регистрация путей"""
    router = app.router
    s = site_handler
    f = form_handler
    a = ajax_handler
    t = token_handler

    router.add_get("/", s.index, name="index")
    router.add_get("/profile", s.profile, name="profile")
    router.add_get("/logout", s.logout, name="logout")
    router.add_get(r"/course/{course_id:\d+}", s.course, name="course")
    router.add_get("/search_courses", s.search_courses, name="search_courses")
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}",
        s.lesson,
        name="lesson",
    )
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/task/{task_id:\d+}",
        s.task,
        name="task",
    )
    router.add_get(
        r"/course/{course_id:\d+}/waiting_solutions",
        s.waiting_solutions,
        name="waiting_solutions",
    )
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}"
        r"/task/{task_id:\d+}/solution/{solution_id:\d+}",
        s.solution,
        name="solution",
    )

    router.add_get("/login", f.login, name="login")
    router.add_post("/login", f.handle_login)
    router.add_get("/register", f.register, name="register")
    router.add_post("/register", f.handle_register)
    router.add_get("/create_course", f.create_course, name="create_course")
    router.add_post("/create_course", f.handle_create_course)
    router.add_get(
        r"/course/{course_id:\d+}/create_lesson",
        f.create_lesson,
        name="create_lesson",
    )
    router.add_post(
        r"/course/{course_id:\d+}/create_lesson",
        f.handle_create_lesson,
    )
    router.add_get(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task",
        f.create_task,
        name="create_task",
    )
    router.add_post(
        r"/course/{course_id:\d+}/lesson/{lesson_id:\d+}/create_task",
        f.handle_create_task,
    )
    router.add_get(
        "/activate_course_invite",
        f.activate_course_invite,
        name="activate_course_invite",
    )

    router.add_post(r"/subscribe/{course_id:\d+}", a.handle_course_subscribe)
    router.add_post(r"/search_courses", a.handler_search_courses)
    router.add_post(
        r"/delete_course/{course_id:\d+}",
        a.delete_course,
        name="delete_course",
    )
    router.add_post(r"/submit_solution/{task_id:\d+}", a.handle_task_solution)
    router.add_post("/mark_solution", a.mark_solution)

    router.add_post("/create_token_confirmation", t.create_token_confirmation)
    router.add_post("/check_register_data_indentity", t.check_register_data_indentity)
    router.add_post("/confirm_course_invite", t.confirm_course_invite)

    router.add_static("/static/", path=config.STATIC_PATH, name="static")
