"""Модуль с моделями пользователя.

Есть модель для зарегестрированного на сайте пользоваля, и анонимного.
"""

import hashlib
from enum import IntEnum
from typing import Optional

from tortoise.models import Model
from tortoise import fields


class UserRole(IntEnum):
    """Тип пользователя - ученик или учитель."""

    STUDENT = 0
    TEACHER = 1

    @classmethod
    def get_by_role_name(cls, role_name: str) -> "UserRole":
        """Получение экземпляра класса по названию роли."""
        role = {
            "student": cls.STUDENT,
            "teacher": cls.TEACHER,
        }.get(role_name)
        if role is None:
            raise ValueError()
        return role

    def get_role_name(self) -> str:
        """Получение роли в качестве русского названия."""
        return {
            UserRole.STUDENT: "ученик",
            UserRole.TEACHER: "учитель",
        }[self]


class User(Model):
    """Модель пользователя."""

    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=128, unique=True)
    username = fields.CharField(max_length=32)
    password_hash = fields.CharField(max_length=128)
    role = fields.IntEnumField(UserRole, default=UserRole.STUDENT)

    studied_courses: fields.ManyToManyRelation["Course"]  # noqa: F821
    taught_courses: fields.ReverseRelation["Course"]  # noqa: F821

    is_authenticated = True

    @staticmethod
    async def get_by_id(user_id: int) -> Optional["User"]:
        """Получение пользователя по ID."""
        user = await User.get_or_none(id=user_id)
        return user

    @property
    def is_student(self) -> bool:
        """Является ли пользователь учеником."""
        return self.role == UserRole.STUDENT

    @property
    def is_teacher(self) -> bool:
        """Является ли пользователь учителем."""
        return self.role == UserRole.TEACHER

    @property
    def role_name(self) -> str:
        """
        Получение роли пользователя как слово.
        Например: "ученик" или "учитель"
        """
        return self.role.get_role_name()

    def set_password(self, password: str):
        """Установка пароля пользователю."""
        password_hash = _make_password_hash(password)
        self.password_hash = password_hash

    def set_role(self, role: str):
        """Установка роли пользователю."""
        role = UserRole.get_by_role_name(role)
        self.role = role

    def check_password(self, password: str) -> bool:
        """Проверка на совпадение пароля."""
        password_hash = _make_password_hash(password)
        return self.password_hash == password_hash


def _make_password_hash(password: str) -> str:
    """Создание хэша для пароля пользователя."""
    return hashlib.sha256(password.encode("u8")).hexdigest()


class AnonimousUser:
    """Модель незарегистрированного пользователя."""

    is_authenticated = False
