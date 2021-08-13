from enum import IntEnum

from tortoise.models import Model
from tortoise import fields


class UserRole(IntEnum):
    """Тип пользователя - ученик или учитель"""

    STUDENT = 0
    TEACHER = 1

    @classmethod
    def get_by_role_name(cls, role_name):
        """Получение экземпляра класса по названию роли"""
        if role_name == "student":
            return cls.STUDENT
        elif role_name == "teacher":
            return cls.TEACHER
        else:
            raise ValueError()

    def get_role_name(self):
        """Получение роли в качестве русского названия"""
        if self == UserRole.STUDENT:
            return "ученик"
        elif self == UserRole.TEACHER:
            return "учитель"
        else:
            raise ValueError()


class User(Model):
    """Модель пользователя"""

    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=128, unique=True)
    username = fields.CharField(max_length=32)
    password_hash = fields.CharField(max_length=128)
    role = fields.IntEnumField(UserRole, default=UserRole.STUDENT)

    studied_courses: fields.ManyToManyRelation["Course"]  # noqa: F821
    taught_courses: fields.ReverseRelation["Course"]  # noqa: F821

    is_authenticated = True

    @staticmethod
    async def get_by_id(user_id):
        """Получение пользователя по ID"""
        user = await User.get_or_none(id=user_id)
        return user

    @staticmethod
    async def check_password(email, password):
        """Проверка идентичности введённого пароля с паролей аккаунта"""
        user = await User.get_or_none(email=email)
        if user is None:
            return False
        return user.password == password

    @property
    def is_student(self):
        """Является ли пользователь учеником"""
        return self.role == UserRole.STUDENT

    @property
    def is_teacher(self):
        """Является ли пользователь учителем"""
        return self.role == UserRole.TEACHER

    @property
    def role_name(self):
        """
        Получение роли пользователя как слово.
        Например: "ученик" или "учитель"
        """
        return self.role.get_role_name()


class AnonimousUser:
    """Модель незарегистрированного пользователя"""

    is_authenticated = False
