from django.db import models
from .question import Question
from .tag import Tag
from base.models import BaseModel


class Option(BaseModel):

    class Meta:
        verbose_name = "Option"
        verbose_name_plural = "Options"

        db_table = "Options"

        ordering = ["question__order", "order"]

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="Question",
    )
    text = models.TextField(max_length=200, verbose_name="Answer")
    image_url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Image URL",
        help_text="requires image link",
    )
    tags = models.ManyToManyField(Tag, verbose_name="Tags")
    order = models.IntegerField(default=0, verbose_name="Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    def __str__(self):
        return self.text
