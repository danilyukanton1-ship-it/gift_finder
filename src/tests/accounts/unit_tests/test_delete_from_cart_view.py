from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from gifts.models import Product, Direction, Tag
from accounts.models import Cart


class DeleteFromCartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test",
            email="123@example.com",
            password="Test1234",
        )
        self.user_2 = User.objects.create_user(
            username="test2",
            email="0987@example.com",
            password="Test8765",
        )
        self.tag_child = Tag.objects.create(name="child")
        self.direction = Direction.objects.create(
            name="Test Direction",
            description="Test Direction Description",
            order=1,
        )
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
        self.cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1,
            is_purchased=False,
        )
        self.path = reverse(
            "accounts:delete_from_cart", kwargs={"item_id": self.cart_item.id}
        )
        self.login_url = reverse("accounts:login")
        self.cart_url = reverse("accounts:cart")

    def _login(self):
        return self.client.login(username="test", password="Test1234")

    def test_delete_from_cart_if_unauthenticated(self):
        response = self.client.post(self.path, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_delete_from_cart_deletes_the_item(self):
        """delete item if it exists"""
        self._login()

        response = self.client.post(self.path, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.cart_url)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

    def test_delete_from_cart_if_product_does_not_exist(self):
        """delete item if it does not exist"""
        self._login()
        path = reverse("accounts:delete_from_cart", kwargs={"item_id": 9000})
        response = self.client.post(path, follow=True)

        self.assertEqual(response.status_code, 404)

    def test_delete_from_cart_delete_item_from_other_user(self):
        """delete item if other user's item"""
        self._login()
        other_cart_item = Cart.objects.create(
            user=self.user_2,
            product=self.product,
            quantity=1,
            is_purchased=False,
        )
        path = reverse(
            "accounts:delete_from_cart", kwargs={"item_id": other_cart_item.id}
        )
        response = self.client.post(path, follow=False)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Cart.objects.filter(id=other_cart_item.id).exists())
