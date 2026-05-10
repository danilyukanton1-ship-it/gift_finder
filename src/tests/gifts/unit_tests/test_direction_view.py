from django.test import TestCase, Client
from gifts.models import Direction, Question, Option, Tag
from django.urls import reverse
from unittest.mock import patch, MagicMock


class DirectionViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.path = reverse("gifts:directions")
        self.tag_child = Tag.objects.create(name="child")
        self.direction = Direction.objects.create(
            name="Test Direction",
            description="Test Direction Description",
            order=1,
        )
        self.direction.tags.add(self.tag_child)

        self.direction_2 = Direction.objects.create(
            name="Test Direction 2",
            description="Test Direction 2 Description",
            order=2,
        )
        self.direction_2.tags.add(self.tag_child)

        self.question = Question.objects.create(
            text="What is your favorite color?",
            question_type=Question.QuestionTypes.SINGLE,
            order=1,
            is_active=True,
            status=Question.QuestionStatus.REQUIRED,
        )
        self.option = Option.objects.create(
            text="Option 1",
            question=self.question,
            order=1,
            is_active=True,
        )
        self.option.tags.add(self.tag_child)

    def _set_session_options(self, option_ids):
        session = self.client.session
        session["selected_options"] = option_ids
        session.save()

    def test_get_direction_with_session_data(self):
        """GET with selected options in session"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value

            expected_data = [
                {
                    "direction": self.direction,
                    "products_count": 5,
                    "top_products": [],
                }
            ]

            mock_instance.process_service.return_value = (None, expected_data, True)
            self._set_session_options(["1", "2", "3"])
            response = self.client.get(self.path)

            MockService.assert_called_once_with(response.wsgi_request, ["1", "2", "3"])

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "gifts/directions.html")
            self.assertEqual(response.context["directions_data"], expected_data)

    def test_get_directions_with_empty_session_data(self):
        """GET with empty session data"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value

            self._set_session_options([])

            expected_data = []
            mock_instance.process_service.return_value = (None, expected_data, True)

            response = self.client.get(self.path)

            MockService.assert_called_once_with(response.wsgi_request, [])
            self.assertEqual(response.status_code, 200)

    def test_get_direction_without_session_data(self):
        """GET without session data"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)
            response = self.client.get(self.path)
            MockService.assert_called_once_with(response.wsgi_request, [])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["directions_data"], [])

    def test_get_direction_with_many_directions_in_session(self):
        """GET with many directions in session"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value

            expected_data = [
                {
                    "direction": self.direction,
                    "products_count": 10,
                    "top_products": [
                        {"product": {"name": "iPhone 15"}},
                        {"product": {"name": "MacBook Pro"}},
                    ],
                },
                {
                    "direction": self.direction_2,
                    "products_count": 3,
                    "top_products": [
                        {"product": {"name": "Django Book"}},
                    ],
                },
            ]
            mock_instance.process_service.return_value = (None, expected_data, True)

            self._set_session_options(["1", "2", "3"])
            response = self.client.get(self.path)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["directions_data"]), 2)
            self.assertEqual(
                response.context["directions_data"][0]["direction"].name,
                "Test Direction",
            )
            self.assertEqual(
                response.context["directions_data"][1]["direction"].name,
                "Test Direction 2",
            )

    def test_get_direction_with_top_products(self):
        """GET with top products(checking)"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            expected_data = [
                {
                    "direction": self.direction,
                    "products_count": 10,
                    "top_products": [
                        {"product": {"name": "iPhone 15"}},
                        {"product": {"name": "MacBook Pro"}},
                    ],
                },
            ]
            mock_instance.process_service.return_value = (None, expected_data, True)

            self._set_session_options(["1"])
            response = self.client.get(self.path)

            top_products = response.context["directions_data"][0]["top_products"]
            self.assertEqual(len(top_products), 2)
            self.assertEqual(top_products[0]["product"]["name"], "iPhone 15")
            self.assertEqual(top_products[1]["product"]["name"], "MacBook Pro")

    def test_get_direction_redirect(self):
        """GET with redirect"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value

            from django.http import HttpResponseRedirect

            fake_redirect = HttpResponseRedirect("/login/")
            mock_instance.process_service.return_value = (fake_redirect, [], True)

            self._set_session_options(["1"])
            response = self.client.get(self.path)

            self.assertEqual(response.status_code, 302)

    def test_get_direction_if_many_options(self):
        """GET with many options"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)

            l_list = [str(number) for number in range(1, 101)]
            self._set_session_options(l_list)
            response = self.client.get(self.path)
            MockService.assert_called_once_with(response.wsgi_request, l_list)
            self.assertEqual(response.status_code, 200)

    def test_get_direction_does_not_modify_session(self):
        """GET dies not modify session data?"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            expected_data = [
                {
                    "direction": self.direction,
                    "products_count": 10,
                    "top_products": [
                        {"product": {"name": "iPhone 15"}},
                        {"product": {"name": "MacBook Pro"}},
                    ],
                },
            ]
            mock_instance.process_service.return_value = (None, expected_data, True)

            options = ["1", "2", "3"]
            self._set_session_options(options)
            response = self.client.get(self.path)
            session = self.client.session
            self.assertEqual(session.get("selected_options"), options)

    def test_get_directions_session_after_redirect(self):
        """session changed after redirect?"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            from django.http import HttpResponseRedirect

            fake_redirect = HttpResponseRedirect("/login/")
            mock_instance.process_service.return_value = (fake_redirect, [], True)
            options = ["1", "2", "3"]
            self._set_session_options(options)
            response = self.client.get(self.path)
            session = self.client.session
            self.assertEqual(session.get("selected_options"), options)

    def test_get_direction_if_malformed_session_data(self):
        """session with incorrect data type"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)

            session = self.client.session
            session["selected_options"] = "effefef"
            session.save()

            response = self.client.get(self.path)

            MockService.assert_called_once_with(response.wsgi_request, [])
            self.assertEqual(response.status_code, 200)

    def test_get_direction_if_not_in_session(self):
        """selected options not in session"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)

            response = self.client.get(self.path)

            MockService.assert_called_once_with(response.wsgi_request, [])
            self.assertEqual(response.status_code, 200)

    def test_get_direction_if_options_is_none(self):
        """selected options is none"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)

            session = self.client.session
            session["selected_options"] = None
            session.save()

            response = self.client.get(self.path)
            MockService.assert_called_once_with(response.wsgi_request, [])
            self.assertEqual(response.status_code, 200)

    def test_get_direction_with_correct_template(self):
        """correct template is returned"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)
            response = self.client.get(self.path)
            self.assertTemplateUsed(response, "gifts/directions.html")

    def test_get_direction_with_correct_keys_in_context(self):
        """context with correct keys are returned"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)

            response = self.client.get(self.path)

            self.assertIn("directions_data", response.context)

    def test_get_direction_with_correct_expected_data(self):
        """correct expected data is returned"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            expected_data = [
                {
                    "direction": self.direction,
                    "products_count": 5,
                    "top_products": [
                        {"product": {"name": "Test Product", "price": 99}}
                    ],
                }
            ]
            mock_instance.process_service.return_value = (None, expected_data, True)
            self._set_session_options(["1"])
            response = self.client.get(self.path)

            data = response.context["directions_data"][0]
            self.assertTrue(hasattr(data["direction"], "name"))
            self.assertTrue(hasattr(data["direction"], "description"))
            self.assertIsInstance(data["products_count"], int)
            self.assertIsInstance(data["top_products"], list)

    def test_get_direction_full_workflow(self):
        """full workflow get directions"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            expected_data = [
                {
                    "direction": self.direction,
                    "products_count": 5,
                    "top_products": [
                        {"product": {"name": "Test Product", "price": 99}}
                    ],
                }
            ]
            mock_instance.process_service.return_value = (None, expected_data, True)

            self._set_session_options(["1", "2"])
            response = self.client.get(self.path)

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "gifts/directions.html")
            self.assertEqual(len(response.context["directions_data"]), 1)

    def test_get_direction_full_workflow_with_empty_data(self):
        """full workflow with empty data get directions"""
        with patch("gifts.views.DirectionViewService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.process_service.return_value = (None, [], True)

            response = self.client.get(self.path)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["directions_data"]), 0)
