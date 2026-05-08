from gifts.models import Question, Option


class QuestionViewService:
    """For question related operations in views"""

    @staticmethod
    def get_active_questions():
        question = Question.objects.filter(is_active=True).order_by("order")
        return question

    @staticmethod
    def extract_selected(request_data, questions):
        selected_options = []

        for question in questions:
            answer_key = f"question_{question.id}"

            if answer_key not in request_data:
                continue

            if question.question_type == "multiple":
                selected_options.extend(request_data.getlist(answer_key))
            else:
                selected_options.append(request_data.get(answer_key))

        return selected_options

    @staticmethod
    def has_child_tag(selected_options):
        if not selected_options:
            return False
        return Option.objects.filter(
            id__in=selected_options, tags__name="child"
        ).exists()

    @staticmethod
    def get_mandatory_questions(selected_options):

        if QuestionViewService.has_child_tag(selected_options):
            return set(
                Question.objects.filter(is_active=True).values_list("id", flat=True)
            )
        else:
            return set(
                Question.objects.filter(
                    is_active=True, status=Question.QuestionStatus.REQUIRED
                ).values_list("id", flat=True)
            )

    @staticmethod
    def validate_answer(selected_options, questions):
        mandatory_questions = QuestionViewService.get_mandatory_questions(
            selected_options
        )
        answered_questions = set()
        if selected_options:
            options = Option.objects.filter(id__in=selected_options).select_related(
                "question"
            )
            for option in options:
                answered_questions.add(option.question.id)
        return mandatory_questions == answered_questions
