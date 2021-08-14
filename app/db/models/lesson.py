"""Модуль с моделью урока курса."""

from tortoise.models import Model
from tortoise import fields


class Lesson(Model):
    """Модель урока курса."""

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=64)
    order_index = fields.IntField()

    course = fields.ForeignKeyField("models.Course", related_name="lessons")

    tasks: fields.ReverseRelation["Task"]  # noqa: F821
