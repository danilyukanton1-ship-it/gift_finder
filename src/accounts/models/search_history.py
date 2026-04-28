from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from gifts.models import Option


class SearchHistory(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    options = models.ManyToManyField(Option, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'
