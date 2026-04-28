from django.db import models
from django.contrib.auth.models import User
from gifts.models import Product
from base.models import BaseModel


class Cart(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(default=1)

    is_purchased = models.BooleanField(default=False, verbose_name="Is purchased")

    note = models.TextField(null=True, blank=True, verbose_name="Note")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product", "is_purchased"],
                name="unique_user_product_active",
            )
        ]
