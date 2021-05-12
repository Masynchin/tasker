from tortoise.models import Model
from tortoise import fields


class Task(Model):
    """Модель задачи урока"""

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=32)
    condition = fields.TextField()
    example = fields.TextField()
    order_index = fields.IntField()

    lesson = fields.ForeignKeyField("models.Lesson", related_name="tasks")

    solutions: fields.ReverseRelation["models.TaskSolution"]
