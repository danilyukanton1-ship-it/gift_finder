from gifts.models import Product, Direction, Tag
from django.test import TestCase, Client
from django.urls import reverse


class ProductViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.tag_1 = Tag.objects.create(name="test")
        self.tag_2 = Tag.objects.create(name="child")
        self.direction = Direction.objects.create(
            id=1,
            name="Test Direction",
            description="Test Direction Description",
            order=1,
        )
        self.direction.tags.add(self.tag_1, self.tag_2)
        self.path = reverse(
            "gifts:products", kwargs={"direction_id": self.direction.id}
        )

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
        self.product_1.tags.add(self.tag_1)
        self.product_2 = Product.objects.create(
            id=2,
            name="Test Product 2",
            price=200,
            currency=Product.Currency.USD,
            description="Test Product 2 Description",
            direction=self.direction,
            reviews_count=8,
            in_stock=True,
        )
        self.product_2.tags.add(self.tag_2)

    def _set_session_products(self, products):
        session = self.client.session
        session["all_products"] = products
        session.save()

    def test_product_view_with_valid_data(self):
        """with valid data"""

        products_data = {
            str(self.direction.id): {
                "direction_name": self.direction.name,
                "products": [
                    {
                        "product_id": self.product_1.id,
                        "product_name": self.product_1.name,
                        "product_price": self.product_1.price,
                        "product_currency": self.product_1.currency,
                        "normalized_score": 85,
                    },
                    {
                        "product_id": self.product_2.id,
                        "product_name": self.product_2.name,
                        "product_price": self.product_2.price,
                        "product_currency": self.product_2.currency,
                        "normalized_score": 90,
                    },
                ],
            }
        }
        self._set_session_products(products_data)

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/products.html")
        self.assertIn("products_data", response.context)
        self.assertEqual(len(response.context["products_data"]), 2)
        self.assertEqual(response.context["direction_id"], self.direction.id)
        self.assertEqual(response.context["direction_name"], self.direction.name)
        self.assertEqual(
            response.context["products_data"][0]["product_name"], "Test Product 1"
        )
        self.assertEqual(
            response.context["products_data"][1]["product_name"], "Test Product 2"
        )

    def test_product_view_without_session_data(self):
        """without session data"""

        response = self.client.get(self.path, follow=False)
        self.assertEqual(response.status_code, 302)

    def test_product_view_with_empty_session_data(self):
        """with empty session data"""
        self._set_session_products({})
        response = self.client.get(self.path, follow=False)
        self.assertEqual(response.status_code, 302)

    def test_product_view_with_empty_products_in_session_data(self):
        """with empty products in session data"""
        products_data = {
            str(self.direction.id): {
                "direction_name": self.direction.name,
                "products": [],
            }
        }
        self._set_session_products(products_data)
        response = self.client.get(self.path, follow=False)
        self.assertEqual(response.status_code, 302)

    def test_product_view_with_full_data_products(self):
        """product with full data"""
        products_data = {
            str(self.direction.id): {
                "direction_name": self.direction.name,
                "products": [
                    {
                        "product_id": self.product_1.id,
                        "product_name": self.product_1.name,
                        "product_price": float(self.product_1.price),
                        "product_currency": self.product_1.currency,
                        "product_image_url": None,
                        "product_url": "https://example.com/product1",
                        "product_rating": 4.5,
                        "product_source": "Amazon",
                        "normalized_score": 85.0,
                    },
                    {
                        "product_id": self.product_2.id,
                        "product_name": self.product_2.name,
                        "product_price": float(self.product_2.price),
                        "product_currency": self.product_2.currency,
                        "product_image_url": None,
                        "product_url": "https://example.com/product2",
                        "product_rating": 4.8,
                        "product_source": "Amazon",
                        "normalized_score": 92.0,
                    },
                ],
            }
        }
        self._set_session_products(products_data)
        response = self.client.get(self.path, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/products.html")
        self.assertEqual(len(response.context["products_data"]), 2)
        self.assertEqual(
            response.context["products_data"][0]["product_url"],
            "https://example.com/product1",
        )
        self.assertEqual(
            response.context["products_data"][0]["product_image_url"],
            None,
        )
        self.assertEqual(
            response.context["products_data"][0]["product_source"],
            "Amazon",
        )
        self.assertEqual(response.context["products_data"][0]["normalized_score"], 85.0)
        self.assertEqual(response.context["products_data"][0]["product_rating"], 4.5)

    def test_product_view_with_wrong_direction_id_in_data(self):
        """with wrong direction id"""
        products_data = {
            str(100): {
                "direction_name": self.direction.name,
                "products": [
                    {
                        "product_id": self.product_1.id,
                        "product_name": self.product_1.name,
                        "product_price": self.product_1.price,
                        "product_currency": self.product_1.currency,
                        "normalized_score": 85,
                    },
                    {
                        "product_id": self.product_2.id,
                        "product_name": self.product_2.name,
                        "product_price": self.product_2.price,
                        "product_currency": self.product_2.currency,
                        "normalized_score": 90,
                    },
                ],
            }
        }
        self._set_session_products(products_data)
        response = self.client.get(self.path, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gifts:directions"))
