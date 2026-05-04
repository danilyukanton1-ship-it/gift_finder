from gifts.models import Question


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
