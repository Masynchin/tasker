"""Модуль с собственными исключениями."""


class IncorrectPassword(Exception):
    """Некорректный пароль для аккаунта данного пользователя."""


class NotUniqueEmail(Exception):
    """Не уникальная почта пользователя."""


class UserDoesNotExist(Exception):
    """Пользователь с данной почтой не существует."""


class CourseDoesNotExist(Exception):
    """Курс с данным ID не существует."""


class NotEnoughAccessRights(Exception):
    """Нет прав доступа к данной странице."""


class LessonDoesNotExist(Exception):
    """Урок с данным ID не существует."""


class InvalidCourseInvite(Exception):
    """Неверный токен для приглашения в курс."""


class TaskDoesNotExist(Exception):
    """Задача с данным ID не существует."""


class SolutionDoesNotExist(Exception):
    """Решения задачи с данным ID не существует."""
