from enum import IntEnum

from tortoise.models import Model
from tortoise import fields


class TaskSolutionStatus(IntEnum):
    """Статус решения - ожидает просмотра, не зачтено, зачтено"""

    WAITING = 1
    INCORRECT = 2
    CORRECT = 3

    @property
    def is_incorrect(self):
        return self == TaskSolutionStatus.INCORRECT

    def as_text(self):
        """Получение статуса текстом"""
        if self == TaskSolutionStatus.WAITING:
            return "Ожидает просмотра"
        elif self == TaskSolutionStatus.INCORRECT:
            return "Не засчитано"
        elif self == TaskSolutionStatus.CORRECT:
            return "Засчитано"
        else:
            raise ValueError()


class TaskSolution(Model):
    """Модель решения задачи"""

    content = fields.TextField()
    extension = fields.CharField(max_length=8)
    status = fields.IntEnumField(
        TaskSolutionStatus,
        default=TaskSolutionStatus.WAITING,
    )
    timestamp = fields.DatetimeField(auto_now=True)

    student = fields.ForeignKeyField("models.User", related_name="solutions")
    task = fields.ForeignKeyField("models.Task", related_name="solutions")

    class Meta:
        unique_together = ("student", "task")