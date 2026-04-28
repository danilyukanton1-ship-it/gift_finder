from django.utils import timezone

from django.db import models


class BaseModel(models.Model):

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
