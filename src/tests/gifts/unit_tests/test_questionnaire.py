from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from gifts.models import Question, Option, Tag
from gifts.services.question_view_services import QuestionViewService


class QuestionnaireTest(TestCase):

    def setUp(self):

        self.path = reverse("gifts:questionnaire")
        self.client = Client()
        self.tag1 = Tag.objects.create(name="Tag 1")
        self.tag2 = Tag.objects.create(name="child")
        self.tag3 = Tag.objects.create(name="Tag 3")
        self.tag4 = Tag.objects.create(name="Tag 4")
        self.tag5 = Tag.objects.create(name="Tag 5")
        self.tag6 = Tag.objects.create(name="Tag 6")
        self.tag7 = Tag.objects.create(name="Tag 7")
        self.tag8 = Tag.objects.create(name="Tag 8")

        self.question_1 = Question.objects.create(
            text="Question 1",
            question_type=Question.QuestionTypes.SINGLE,
            order=1,
            is_active=True,
            is_required=True,
        )

        self.question_2 = Question.objects.create(
            text="Question 2",
            question_type=Question.QuestionTypes.MULTIPLE,
            order=6,
            is_active=True,
            is_required=False,
        )

        self.option_1 = Option.objects.create(
            text="Option 1",
            question=self.question_1,
            order=1,
            is_active=True,
        )
        self.option_1.tags.add(self.tag1, self.tag2)

        self.option_2 = Option.objects.create(
            text="Option 2",
            question=self.question_1,
            order=2,
            is_active=True,
        )
        self.option_2.tags.add(self.tag3, self.tag4)

        self.option_3 = Option.objects.create(
            text="Option 3",
            question=self.question_2,
            order=1,
            is_active=True,
        )
        self.option_3.tags.add(self.tag5, self.tag6)
        self.option_4 = Option.objects.create(
            text="Option 4",
            question=self.question_2,
            order=2,
            is_active=True,
        )
        self.option_4.tags.add(self.tag7, self.tag8)

    def test_get_questionnaire(self):
        """Check if get_questionnaire returns correct status 200"""
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_get_questionnaire_with_template(self):
        """Check if get_questionnaire uses correct template"""
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, "gifts/questionnaire.html")

    def test_get_questionnaire_with_active_questions(self):
        """Check if get_questionnaire returns only active questions"""
        inactive_question = Question.objects.create(
            text="Question 10",
            question_type=Question.QuestionTypes.SINGLE,
            order=1,
            is_active=False,
        )
        response = self.client.get(self.path)
        questions = response.context["questions"]
        self.assertIn(self.question_1, questions)
        self.assertIn(self.question_2, questions)
        self.assertNotIn(inactive_question, questions)

    def test_get_questionnaire_with_right_order(self):
        """Check if get_questionnaire returns questions ordered correctly"""
        response = self.client.get(self.path)
        questions = response.context["questions"]
        self.assertEqual(questions[0], self.question_1)
        self.assertEqual(questions[1], self.question_2)

    def test_get_questionnaire_with_all_options(self):
        """Check if get_questionnaire returns questions with their options"""
        response = self.client.get(self.path)
        questions = response.context["questions"]

        options_q1 = questions.get(id=self.question_1.id).options.all()
        self.assertIn(self.option_1, options_q1)
        self.assertIn(self.option_2, options_q1)
        self.assertNotIn(self.option_3, options_q1)
        self.assertNotIn(self.option_4, options_q1)

    # POST tests
    def test_post_valid_data_redirect(self):
        """Check if POST method redirects with correct data"""
        post_data = {
            f"question_{self.question_1.id}": self.option_1.id,
            f"question_{self.question_2.id}": self.option_3.id,
        }

        response = self.client.post(self.path, data=post_data)

        self.assertRedirects(response, reverse("gifts:directions"))

    def test_post_saves_selected_options_to_session(self):
        """Check if POST method saves selected options to session"""
        post_data = {
            f"question_{self.question_1.id}": self.option_1.id,
            f"question_{self.question_2.id}": self.option_3.id,
        }
        response = self.client.post(self.path, data=post_data)

        session = self.client.session
        selected_options = session.get("selected_options", [])
        self.assertIn(str(self.option_1.id), selected_options)
        self.assertIn(str(self.option_3.id), selected_options)
        self.assertEqual(len(selected_options), 2)

    def test_post_with_not_full_data(self):
        """Check if POST with partial data redirects (doesn't validate)"""
        post_data = {
            f"question_{self.question_1.id}": self.option_1.id,
        }
        response = self.client.post(self.path, post_data)

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("selected_options", self.client.session)

    def test_post_with_empty_data(self):
        """Check if POST with empty data redirects"""
        response = self.client.post(self.path, {}, follow=False)

        self.assertEqual(response.status_code, 400)

        session = self.client.session
        self.assertNotIn("selected_options", session)

    # full integration tests

    def test_full_questionnaire_working(self):
        """Full working scenario with valid data"""
        get_response = self.client.get(self.path)
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("questions", get_response.context)

        post_data = {
            f"question_{self.question_1.id}": self.option_1.id,
            f"question_{self.question_2.id}": self.option_3.id,
        }
        post_response = self.client.post(self.path, data=post_data)

        self.assertRedirects(post_response, reverse("gifts:directions"))

        session = self.client.session
        selected_options = session.get("selected_options", [])
        self.assertIn(str(self.option_1.id), selected_options)
        self.assertIn(str(self.option_3.id), selected_options)
        self.assertEqual(len(selected_options), 2)
