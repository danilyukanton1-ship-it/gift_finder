from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from gifts.models import Option


class SavedSearch(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_searches",
        verbose_name="User",
    )

    name = models.CharField(
        max_length=100,
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
        related_name="saved_searches",
    )

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        verbose_name = "Saved Search"
        verbose_name_plural = "Saved Searches"
        ordering = ("-created_at",)
        db_table = "accounts_saved_search"
