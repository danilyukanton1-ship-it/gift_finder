from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from gifts.models import Product, Direction, Tag
from accounts.models import Cart


class CartViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test",
            email="123@.com",
            password="1234",
        )
        self.tag_1 = Tag.objects.create(name="test")
        self.tag_2 = Tag.objects.create(name="child")
        self.direction = Direction.objects.create(
            id=1,
            name="Test Direction",
            description="Test Direction Description",
            order=1,
        )
        self.direction.tags.add(self.tag_1, self.tag_2)
        self.product_1 = Product.objects.create(
            id=1,
            name="Test Product 1",
            price=100,
            currency=Product.Currency.USD,
            description="Test Product 1 Description",
            direction=self.direction,
            reviews_count=5,
            in_stock=True,
        )
        self.product_1.tags.add(self.tag_1, self.tag_2)

        self.path = reverse(
            "gifts:add_to_cart", kwargs={"product_id": self.product_1.id}
        )
        self.cart_url = reverse("accounts:cart")
        self.login_url = reverse("accounts:login")

    def _login(self):
        self.client.login(username="test", password="1234")

    def test_add_to_cart_view_unauthenticated(self):
        """unauthenticated user cannot add items to cart and redirect to /login/"""
        response = self.client.get(self.path, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_add_to_cart_view_new_product_to_cart(self):
        """add new product to cart and redirect to /cart/"""
        self._login()

        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

        response = self.client.post(self.path, follow=False)

        self.assertRedirects(response, self.cart_url)

        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

        cart_item = Cart.objects.get(user=self.user, product=self.product_1)
        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(cart_item.product.price, 100)
        self.assertFalse(cart_item.is_purchased)
        self.assertEqual(cart_item.product.description, "Test Product 1 Description")
        self.assertEqual(cart_item.product.direction, self.direction)
        self.assertEqual(cart_item.product.reviews_count, 5)
        self.assertEqual(cart_item.product.in_stock, True)
        self.assertEqual(cart_item.product.name, "Test Product 1")
        self.assertEqual(cart_item.product.currency, Product.Currency.USD)
        self.assertEqual(cart_item.product.id, 1)

    def test_add_to_cart_increase_quantity_if_product_in_cart(self):
        """if product already in cart, increase quantity"""
        self._login()

        Cart.objects.create(
            user=self.user, product=self.product_1, quantity=1, is_purchased=False
        )

        response = self.client.post(self.path, follow=False)

        self.assertRedirects(response, self.cart_url)

        cart_item = Cart.objects.get(user=self.user, product=self.product_1)
        self.assertEqual(cart_item.quantity, 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("quantity increased", messages[0].message)

    def test_add_to_cart_returns_404_for_nonexistent_product(self):
        """if product does not exist, return 404 status code"""
        self._login()

        invalid_path = reverse("gifts:add_to_cart", kwargs={"product_id": 99999})
        response = self.client.post(invalid_path, follow=False)
        self.assertEqual(response.status_code, 404)

    def test_add_to_cart_returns_405_if_get_method(self):
        """if get method, returns 405 status code"""
        self._login()

        response = self.client.get(self.path, follow=False)

        self.assertEqual(response.status_code, 405)

        response = self.client.put(self.path, follow=False)
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(self.path, follow=False)
        self.assertEqual(response.status_code, 405)

    def test_add_to_cart_if_product_already_purchased(self):
        """if product already purchased, cannot add again - show warning"""
        self._login()

        purchased_item = Cart.objects.create(
            user=self.user, product=self.product_1, quantity=1, is_purchased=True
        )

        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

        response = self.client.post(self.path, follow=False)

        self.assertRedirects(response, reverse("accounts:cart"))

        active_items = Cart.objects.filter(
            user=self.user, product=self.product_1, is_purchased=False
        )
        self.assertEqual(active_items.count(), 0)

        purchased_item.refresh_from_db()
        self.assertEqual(purchased_item.quantity, 1)
        self.assertTrue(purchased_item.is_purchased)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("purchased", messages[0].message.lower())

    def test_add_to_cart_multiple_different_products(self):
        """add different products -> different data"""
        self._login()

        product_2 = Product.objects.create(
            id=2,
            name="Test Product 2",
            description="Test Product 2 Description",
            direction=self.direction,
            price=200,
            currency=Product.Currency.USD,
            in_stock=True,
            reviews_count=6,
        )

        path_2 = reverse("gifts:add_to_cart", kwargs={"product_id": product_2.id})

        self.client.post(self.path, follow=False)
        self.client.post(path_2, follow=False)

        cart_items = Cart.objects.filter(user=self.user, is_purchased=False)
        self.assertEqual(len(cart_items), 2)
        self.assertTrue(cart_items.filter(product=self.product_1).exists())
        self.assertTrue(cart_items.filter(product=product_2).exists())

    def test_add_to_cart_does_not_affect_other_session_data(self):
        """add products -> session data does not change"""
        self._login()

        session = self.client.session
        session["test_data"] = "should_persist"
        session.save()

        response = self.client.post(self.path, follow=False)

        session = self.client.session
        self.assertEqual(session["test_data"], "should_persist")

    def test_add_tp_cart_redirect_to_correct_url(self):
        """redirect to account:cart"""
        self._login()

        response = self.client.post(self.path, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.cart_url)
