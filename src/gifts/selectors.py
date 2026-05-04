from gifts.models import Option, Question, Product


def options_fetch(options_ids):
    return (
        Option.objects.prefetch_related("tags", "question__tags")
        .select_related("question")
        .filter(id__in=options_ids)
    )


def question_get_by_order(order):
    question = Question.objects.get(order=order)
    return question.id


def products_all_with_tags_and_directions():
    return (
        Product.objects.prefetch_related("tags__question")
        .select_related("direction")
        .all()
    )

def all_questions():
    return Question.objects.prefetch_related("tags").select_related("direction").all()
