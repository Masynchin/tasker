"""Модуль с моделью курса."""

from tortoise.models import Model
from tortoise import fields


class Course(Model):
    """Модель курса."""

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=64)
    description = fields.CharField(max_length=128)
    is_private = fields.BooleanField()

    students = fields.ManyToManyField(
        "models.User", related_name="studied_courses"
    )
    teacher = fields.ForeignKeyField(
        "models.User", related_name="taught_courses"
    )

    lessons: fields.ReverseRelation["Lesson"]  # noqa: F821
