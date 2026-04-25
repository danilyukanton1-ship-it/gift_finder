from django.db import models
from .tag import Tag

class Direction(models.Model):

    class Meta:
        verbose_name = 'Direction'
        verbose_name_plural = 'Directions'

        db_table = 'Directions'

        ordering = ['order', 'name']


    name = models.CharField(max_length=100, verbose_name='Name of direction')
    description = models.TextField(max_length=500, verbose_name='Description')
    image_url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Image URL',
        help_text='requires image link'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Tags')
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Parent ID',
        related_name='children'
    )
    order = models.IntegerField(default=0, verbose_name='Order')

    def __str__(self):
        return self.name