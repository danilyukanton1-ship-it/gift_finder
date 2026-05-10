from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterViewTest(TestCase):

    def setUp(self):
        self.path = reverse("accounts:register")
        self.client = Client()
        self.login_url = reverse("accounts:login")

    def test_register_view_returns_200(self):
        """Get returns 200 and correct template"""
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], UserCreationForm)

    def test_register_post_valid_data_creates_user_and_redirects(self):
        """After post valid data creates user and redirects to login"""
        user_count_before = User.objects.count()
        data = {
            "username": "test",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        }
        response = self.client.post(self.path, data)
        self.assertRedirects(response, self.login_url)

        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertTrue(User.objects.filter(username="test").exists())

    def test_register_post_data_not_valid(self):
        """After post invalid data"""
        user_count_before = User.objects.count()
        data = {
            "username": "test",
            "password1": "StrongPass123",
            "password2": "NotStrongPass123",
        }
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(User.objects.filter(username="test").exists())

    def test_register_post_existing_user(self):
        """After post existing user"""
        User.objects.create_user(username="test", password="1234")

        user_count_before = User.objects.count()

        data = {
            "username": "test",
            "password1": "1234",
            "password2": "1234",
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(User.objects.count(), user_count_before)

        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)
        self.assertIn("username", response.context["form"].errors)

    def test_register_view_post_short_password(self):
        """POST with short password shows error"""
        user_count_before = User.objects.count()

        data = {
            "username": "test",
            "password1": "123",
            "password2": "123",
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), user_count_before)
        self.assertTrue(response.context["form"].errors)

    def test_register_view_post_empty_fields(self):
        """POST with empty fields shows error"""
        user_count_before = User.objects.count()
        data = {
            "username": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), user_count_before)
        self.assertTrue(response.context["form"].errors)

    def test_register_view_post_with_empty_password(self):
        """POST with empty password shows error"""
        user_count_before = User.objects.count()
        data = {
            "username": "test",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), user_count_before)
        self.assertTrue(response.context["form"].errors)
        self.assertIn("password1", response.context["form"].errors)

    def test_register_view_post_with_simple_password(self):
        """POST with simple password shows error"""
        user_count_before = User.objects.count()
        data = {
            "username": "test",
            "password1": "12345678",
            "password2": "12345678",
        }
        response = self.client.post(self.path, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), user_count_before)
        self.assertTrue(response.context["form"].errors)
        self.assertIn("password2", response.context["form"].errors)

    def test_register_view_post_invalid_data_returns_from_with_values(self):
        """POST with invalid data shows error and save entered values"""
        data = {
            "username": "test",
            "password1": "pass1234",
            "password2": "different1234",
        }
        response = self.client.post(self.path, data)

        self.assertEqual(response.context["form"]["username"].value(), "test")
        self.assertEqual(response.context["form"]["password1"].value(), "pass1234")
        self.assertEqual(response.context["form"]["password2"].value(), "different1234")

    def test_register_view_post_valid_data_correct_user(self):
        """POST with valid data creates user with correct data"""
        data = {
            "username": "john_doe",
            "password1": "ComplexPass456!",
            "password2": "ComplexPass456!",
        }
        response = self.client.post(self.path, data)

        self.assertRedirects(response, self.login_url)
        user = User.objects.get(username="john_doe")
        self.assertTrue(user.check_password("ComplexPass456!"))
        self.assertTrue(user.is_active)
