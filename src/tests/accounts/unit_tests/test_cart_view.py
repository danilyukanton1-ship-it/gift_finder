from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Cart
from gifts.models import Tag, Direction, Product


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test", email="123@example.com", password="Test123"
        )
        self.tag_child = Tag.objects.create(name="child")
        self.direction = Direction.objects.create(
            name="Test Direction",
            description="Test Direction Description",
            order=1,
        )
        self.direction.tags.add(self.tag_child)

        self.product = Product.objects.create(
            name="Test Product",
            description="Test Product Description",
            price=10,
            currency=Product.Currency.USD,
            in_stock=True,
            reviews_count=10,
            direction=self.direction,
        )
        self.product.tags.add(self.tag_child)
        self.product_2 = Product.objects.create(
            name="Test Product 2",
            description="Test Product Description 2",
            price=100,
            currency=Product.Currency.USD,
            in_stock=True,
            reviews_count=7,
            direction=self.direction,
        )
        self.product_2.tags.add(self.tag_child)

        self.path = reverse("accounts:cart")
        self.login_url = reverse("accounts:login")

    def _login(self):
        return self.client.login(username="test", password="Test123")

    def test_cart_view_if_unauthenticated(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_cart_view_get_empty_context(self):
        """get cart view returns valid data"""
        self._login()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/cart.html")

        self.assertIn("cart_items", response.context)
        self.assertIn("total", response.context)

        self.assertEqual(len(response.context["cart_items"]), 0)
        self.assertEqual(response.context["total"], 0)

    def test_cart_view_get_one_item_in_context(self):
        """get cart view returns valid data(one item)"""
        self._login()

        cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1,
            is_purchased=False,
        )

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["cart_items"])
        self.assertTrue(response.context["total"])
        self.assertEqual(len(response.context["cart_items"]), 1)
        self.assertEqual(response.context["total"], 10)

    def test_cart_view_get_multiple_items_in_context(self):
        """get cart view returns valid data(multiple items)"""
        self._login()

        cart_item_1 = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1,
            is_purchased=False,
        )
        cart_item_2 = Cart.objects.create(
            user=self.user,
            product=self.product_2,
            quantity=2,
            is_purchased=False,
        )
        response = self.client.get(self.path)

        self.assertTrue(response.context["cart_items"])
        self.assertTrue(response.context["total"])
        self.assertEqual(len(response.context["cart_items"]), 2)
        self.assertEqual(response.context["total"], 210)
        self.assertEqual(response.status_code, 200)

    def test_cart_view_if_product_purchased_product_in_cart(self):
        """get cart view if purchased product"""
        self._login()

        cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1,
            is_purchased=True,
        )
        cart_item_2 = Cart.objects.create(
            user=self.user,
            product=self.product_2,
            quantity=2,
            is_purchased=False,
        )
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["cart_items"])
        self.assertTrue(response.context["total"])
        self.assertEqual(response.context["cart_items"].count(), 1)
        self.assertEqual(response.context["total"], 200)
