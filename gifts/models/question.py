from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Question(models.Model):

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

        db_table = 'Questions'

        ordering = ['text']

    class QuestionTypes(models.TextChoices):
        SINGLE = 'single'
        MULTIPLE = 'multiple'
        TEXT = 'text'

    text = models.TextField(max_length=500, verbose_name='Question')
    description = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Description',
    )
    question_type = models.CharField(
        max_length=10,
        choices=QuestionTypes.choices,
        default=QuestionTypes.MULTIPLE,
        verbose_name='Question Type'
    )
    order = models.IntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    priority = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Priority'
    )

    image_url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Image URL',
        help_text='requires image link'
    )

    def __str__(self):
        return self.text
