from gifts.models import Option, Question, Product


def options_get_from_options_ids(options_ids):
    return Option.objects.filter(id__in=options_ids)

def question_get_by_order(order):
    return Question.objects.filter(order=order).first()

def products_all_with_tags():
    return Product.objects.prefetch_related('tags').all()