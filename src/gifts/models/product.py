from django.db import models
from .direction import Direction
from .tag import Tag
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import BaseModel


class Product(BaseModel):

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

        ordering = ["-created_at"]

        db_table = "Products"

    class Currency(models.TextChoices):
        BYN = "BYN"
        RUB = "RUB"
        USD = "USD"
        EUR = "EUR"

    name = models.CharField(max_length=100, verbose_name="Name of product")
    description = models.TextField(max_length=500, verbose_name="Description")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(
        verbose_name="Currency",
        max_length=3,
        default=Currency.USD,
        choices=Currency.choices,
    )
    image_url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Image URL",
        help_text="requires image link",
    )
    additional_image_url = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name="Additional Image URL",
        help_text="requires image link",
    )
    product_url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Product URL",
        help_text="requires image link",
    )
    source = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Source",
        help_text="requires shop name",
    )
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Directions",
    )
    tags = models.ManyToManyField(Tag, verbose_name="Tags")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    reviews_count = models.IntegerField(verbose_name="Reviews Count")
    in_stock = models.BooleanField(default=False, verbose_name="In stock")
    last_checked = models.DateTimeField(auto_now=True, verbose_name="Last Checked")

    def __str__(self):
        return f"{self.name} - {self.price}"
