from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from gifts.models import Option


class SearchHistory(BaseModel):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="search_histories"
    )

    options = models.ManyToManyField(
        Option, blank=True, related_name="search_histories"
    )

    def __str__(self):
        return f'{self.user.username} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    class Meta:
        verbose_name = "Search History"
        verbose_name_plural = "Search Histories"
        ordering = ("-created_at",)
