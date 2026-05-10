from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from accounts.models import Cart
from gifts.models import Direction, Tag, Product


class UpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test",
            email="123@example.com",
            password="Test1234",
        )
        self.user_2 = User.objects.create_user(
            username="test2",
            email="4321@example.com",
            password="Test21223",
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

        self.cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
            is_purchased=False,
        )
        self.path = reverse(
            "accounts:update_cart", kwargs={"item_id": self.cart_item.id}
        )
        self.cart_url = reverse("accounts:cart")
        self.login_url = reverse("accounts:login")

    def _login(self):
        self.client.login(username="test", password="Test1234")

    def test_update_cart_redirects_login_if_unauthenticated(self):
        """unauthenticated users should redirect to login page"""
        response = self.client.post(self.path, {"quantity": 3}, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_update_cart_update_quantity_if_increased_quantity(self):
        """update quantity if has increased quantity"""
        self._login()
        response = self.client.post(self.path, {"quantity": 10}, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.cart_url)
        self.assertEqual(Cart.objects.all().count(), 1)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 10)

    def test_update_cart_update_quantity_if_decreased_quantity(self):
        """update quantity if has decreased quantity"""
        self._login()

        response = self.client.post(self.path, {"quantity": 1}, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.cart_url)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 1)

    def test_update_cart_update_quantity_to_0_delete_cart_item(self):
        """update quantity if has decreased quantity to 0"""
        self._login()
        response = self.client.post(self.path, {"quantity": 0}, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.cart_url)
        self.assertEqual(Cart.objects.filter(id=self.cart_item.id).count(), 0)

    def test_update_cart_if_product_does_not_exist(self):
        """update quantity if product does not exist"""
        self._login()

        invalid_path = reverse("accounts:update_cart", kwargs={"item_id": 9999})
        response = self.client.post(invalid_path, {"quantity": 3}, follow=False)
        self.assertEqual(response.status_code, 404)

    def test_update_cart_if_item_of_other_user(self):
        """update quantity if item of other user"""
        self._login()

        other_user_cart_item = Cart.objects.create(
            user=self.user_2,
            product=self.product,
            quantity=2,
            is_purchased=False,
        )
        path = reverse(
            "accounts:update_cart", kwargs={"item_id": other_user_cart_item.id}
        )
        response = self.client.post(path, {"quantity": 3}, follow=False)

        self.assertEqual(response.status_code, 404)

    def test_update_cart_if_quantity_is_negative(self):
        """update quantity if quantity is negative"""
        self._login()

        response = self.client.post(self.path, {"quantity": -1}, follow=False)

        self.assertRedirects(response, self.cart_url)

        self.assertEqual(Cart.objects.filter(id=self.cart_item.id).count(), 0)

    def test_update_cart_if_no_quantity_in_response(self):
        """update quantity if no quantity in response"""
        self._login()

        response = self.client.post(self.path, {}, follow=False)

        self.assertRedirects(response, self.cart_url)

        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 1)

    def test_update_cart_if_quantity_is_invalid(self):
        """update quantity if quantity is invalid"""
        self._login()

        response = self.client.post(self.path, {"quantity": "avs"}, follow=False)

        self.assertRedirects(response, self.cart_url)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 1)

    def test_update_cart_does_not_affect_other_cart_items(self):
        """updating one cart does not affect other cart items"""
        self._login()

        product = Product.objects.create(
            name="Test Product 2",
            description="Test Product Description 2",
            price=10,
            currency=Product.Currency.USD,
            in_stock=True,
            direction=self.direction,
            reviews_count=1,
        )
        other_cart_item = Cart.objects.create(
            user=self.user,
            product=product,
            quantity=2,
            is_purchased=False,
        )
        other_quantity = other_cart_item.quantity

        response = self.client.post(self.path, {"quantity": 8}, follow=False)

        self.assertRedirects(response, self.cart_url)

        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 8)

        other_cart_item.refresh_from_db()
        self.assertEqual(other_cart_item.quantity, other_quantity)
