"""Модуль с моделью решения задачи."""

from enum import IntEnum

from tortoise.models import Model
from tortoise import fields


class TaskSolutionStatus(IntEnum):
    """Статус решения - ожидает просмотра, не зачтено, зачтено."""

    WAITING = 1
    INCORRECT = 2
    CORRECT = 3

    @property
    def is_incorrect(self) -> bool:
        """Является ли решение незасчитанным."""
        return self == TaskSolutionStatus.INCORRECT

    def as_text(self) -> str:
        """Получение статуса текстом."""
        return {
            TaskSolutionStatus.WAITING: "Ожидает просмотра",
            TaskSolutionStatus.INCORRECT: "Не засчитано",
            TaskSolutionStatus.CORRECT: "Засчитано",
        }[self]


class TaskSolution(Model):
    """Модель решения задачи."""

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
        """Мета-параметры модели.

        Условие на то, что у одного ученика
        может быть только одно решение.
        """

        unique_together = ("student", "task")

    def set_status(self, is_correct: bool):
        """Установка статуса правильности решению задачи."""
        if is_correct:
            self.status = TaskSolutionStatus.CORRECT
        else:
            self.status = TaskSolutionStatus.INCORRECT
