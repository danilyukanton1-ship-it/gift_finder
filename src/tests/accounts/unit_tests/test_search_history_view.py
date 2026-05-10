from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import SearchHistory
from gifts.models import Question, Option, Tag


class SearchHistoryViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.question_1 = Question.objects.create(
            text="Question 1",
            question_type=Question.QuestionTypes.SINGLE,
            order=1,
            is_active=True,
            status=Question.QuestionStatus.REQUIRED,
        )
        self.tag = Tag.objects.create(
            name="child",
        )

        self.user = User.objects.create_user(
            username="test", email="123@example.com", password="Test123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="oth123@example.com", password="Other123"
        )
        self.option_1 = Option.objects.create(
            text="Option 1",
            question=self.question_1,
            order=1,
            is_active=True,
        )
        self.option_1.tags.add(self.tag)

        self.option_2 = Option.objects.create(
            text="Option 2",
            question=self.question_1,
            order=2,
            is_active=True,
        )
        self.option_2.tags.add(self.tag)
        self.path = reverse("accounts:search_history")
        self.login_url = reverse("accounts:login")

    def _login(self):
        return self.client.login(username="test", password="Test123")

    def _create_search_history(self, count=1):
        for i in range(count):
            history = SearchHistory.objects.create(
                user=self.user,
            )
            history.options.add(self.option_1)
            history.options.add(self.option_2)

    def test_search_history_view_redirects_to_login_if_unauthenticated(self):
        response = self.client.get(self.path, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_search_history_view_with_empty_history(self):
        self._login()

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/search_history.html")
        self.assertIn("search_history", response.context)
        self.assertEqual(response.context["search_history"].count(), 0)

    def test_search_history_view_with_multiple_options(self):
        """search history with multiple options"""
        self._login()

        self._create_search_history(count=6)
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_history"].count(), 6)

    def test_search_history_view_ordered_by_created_at_desc(self):
        """search history with ordered by created_at_desc"""
        self._login()

        import time
        from datetime import datetime, timezone

        history1 = SearchHistory.objects.create(
            user=self.user,
        )
        history1.options.add(self.option_1)
        history1.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        history1.save()

        history2 = SearchHistory.objects.create(
            user=self.user,
        )
        history2.options.add(self.option_2)
        history2.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
        history2.save()

        response = self.client.get(self.path)

        histories = response.context["search_history"]

        self.assertEqual(len(histories), 2)
        self.assertTrue(histories[0].created_at > histories[1].created_at)

        self.assertEqual(histories[0].id, history2.id)
        self.assertEqual(histories[1].id, history1.id)
