from gifts.models import Option, Question, Product


def options_fetch(options_ids):
    return (
        Option.objects.prefetch_related("tags", "question__tags")
        .select_related("question")
        .filter(id__in=options_ids)
    )


def question_get_by_order(order):
    return Question.objects.filter(order=order).first()


def products_all_with_tags_and_directions():
    return (
        Product.objects.prefetch_related("tags__question")
        .select_related("direction")
        .all()
    )
