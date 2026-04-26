from gifts.models import Option



def tags_get_from_options(options_ids):
    options = Option.objects.filter(id__in=options_ids)
    tags_from_options = {}

    for option in options:
        question = option.question
        tags = set(question.tags.all())
        if question in tags_from_options:
            tags_from_options[question] |= tags
        else:
            tags_from_options[question] = tags

    return tags_from_options

