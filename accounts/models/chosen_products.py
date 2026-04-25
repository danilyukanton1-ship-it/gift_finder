from django.db import models
from django.contrib.auth.models import User
from gifts.models import Product

class ChosenProducts(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    selected_at = models.DateTimeField(auto_now_add=True)

    quantity = models.PositiveIntegerField(default=1)

    is_purchased = models.BooleanField(default=False)

    note = models.TextField(null= True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'
