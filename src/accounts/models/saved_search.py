from django.db import models
from django.contrib.auth.models import User
from gifts.models import Option


class SavedSearch(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_search",
        verbose_name="User",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Name of selection",
    )

    description = models.TextField(
        max_length=600,
        verbose_name="Description",
        blank=True,
        null=True,
    )

    options = models.ManyToManyField(
        Option,
        verbose_name="Options",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"
