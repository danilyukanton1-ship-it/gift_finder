from gifts.models import Option

def options_get_from_options_ids(options_ids):
    return Option.objects.filter(id__in=options_ids)


