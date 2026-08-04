from django.db import models

from base.models import BaseModel

from .question import Question


class Tag(BaseModel):
    name = models.CharField(max_length=50, verbose_name="Tag name")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tags",
    )

    def __str__(self):
        return self.name
