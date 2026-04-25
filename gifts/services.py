from .models import Option, Product, Question


def get_min_matches(user_tag_count):
    return max(3, user_tag_count // 4)


def get_tags_from_options(options_ids):
    """
    :param options_ids:
    :return: dict of questions and sets of tags from these questions
    """
    options = Option.objects.filter(id__in=options_ids)
    tags_from_questions = {}

    for option in options:
        question = option.question
        tags = set(option.tags.all())

        if question in tags_from_questions:
            tags_from_questions[question] |= tags
        else:
            tags_from_questions[question] = tags

    return tags_from_questions


def get_mandatory_questions(tags_from_questions):
    """
    :param tags_from_questions:
    :return: returns mandatory questions depends on if user has chosen 'child' or not
    """
    answered_questions = set(q.order for q in tags_from_questions.keys())
    if 2 in answered_questions and 3 in answered_questions:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    return [1, 4, 5, 6, 7, 8, 9, 10]


def product_passes_mandatory_check(product, tags_from_questions, mandatory_list):
    score = 0
    max_score = 0

    for order in mandatory_list:
        question = Question.objects.get(order=order)
        user_tags = tags_from_questions.get(question, set())

        if not user_tags:
            continue

        max_score += question.priority
        product_tags = set(product.tags.filter(question=question))
        matched_count = len(user_tags & product_tags)
        user_count = len(user_tags)

        if user_count > 0:
            score += question.priority * (matched_count / user_count)
        if question.order == 1 or question.order == 6:
            if not user_tags & product_tags:
                return False
    if max_score == 0:
        return True
    return (score / max_score) * 100 > 45


def find_products_and_group_by_direction(tags_by_question):
    # 1. Определяем обязательные вопросы
    answered_orders = set(q.order for q in tags_by_question.keys())
    if 2 in answered_orders and 3 in answered_orders:
        mandatory_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    else:
        mandatory_list = [1, 4, 5, 6, 7, 8, 9, 10]

    # 2. Все теги пользователя
    all_user_tags = set()
    for tags in tags_by_question.values():
        all_user_tags.update(tag.name for tag in tags)

    # 3. Максимальный вес (для сортировки)
    max_weight = 0
    for question, user_tags in tags_by_question.items():
        max_weight += len(user_tags) * question.priority

    # 4. Минимальное количество совпадений (зависит от числа тегов)
    min_matches = get_min_matches(len(all_user_tags))

    products_found = []

    # Первый проход — строгий
    for product in Product.objects.filter(in_stock=True):
        if not product_passes_mandatory_check(product, tags_by_question, mandatory_list):
            continue

        product_tags = set(tag.name for tag in product.tags.all())
        matches = all_user_tags & product_tags
        match_count = len(matches)

        if match_count >= min_matches:
            weight = 0
            for question, user_tags in tags_by_question.items():
                product_question_tags = set(product.tags.filter(question=question))
                matches_q = user_tags & product_question_tags
                weight += len(matches_q) * question.priority

            weight = (weight / max_weight) * 100 if max_weight > 0 else 0

            products_found.append({
                'product': product,
                'weight': weight,
                'matches': list(matches)
            })

    # group by direction
    products_by_direction = {}

    for item in products_found:
        product = item['product']
        direction = product.direction

        if direction.id not in products_by_direction:
            products_by_direction[direction.id] = {
                'direction': direction,
                'products': [],
                'product_count': 0,
                'top_products': []
            }

        products_by_direction[direction.id]['products'].append({
            'product': product,
            'weight_score': item['weight'],
            'matched_tags': item['matches']
        })
        products_by_direction[direction.id]['product_count'] += 1

    # sort
    for data in products_by_direction.values():
        data['products'].sort(key=lambda x: x['weight_score'], reverse=True)
        data['top_products'] = data['products'][:3]

    return products_by_direction


def serialize_products_by_direction(products_by_direction):
    """
    :param products_by_direction:
    :return: serializable list of dirs of products
    """
    serialized = {}
    for dir_id, data in products_by_direction.items():
        serialized_products = []
        for product_data in data['products']:
            serialized_products.append({
                'product_id': product_data['product'].id,
                'product_name': product_data['product'].name,
                'product_price': float(product_data['product'].price),
                'product_currency': product_data['product'].currency,
                'product_source': product_data['product'].source,
                'product_url': product_data['product'].product_url,
                'product_image_url': product_data['product'].image_url,
                'product_rating': float(product_data['product'].rating) if product_data['product'].rating else None,
                'weight_score': product_data['weight_score'],
                'matched_tags': product_data['matched_tags'],
            })

        serialized_top = []
        for product_data in data['top_products']:
            serialized_top.append({
                'product_id': product_data['product'].id,
                'product_name': product_data['product'].name,
                'product_price': float(product_data['product'].price),
                'product_currency': product_data['product'].currency,
                'product_source': product_data['product'].source,
                'product_url': product_data['product'].product_url,
                'product_image_url': product_data['product'].image_url,
                'product_rating': float(product_data['product'].rating) if product_data['product'].rating else None,
                'weight_score': product_data['weight_score'],
                'matched_tags': product_data['matched_tags'],
            })

        serialized[dir_id] = {
            'direction_id': data['direction'].id,
            'direction_name': data['direction'].name,
            'products': serialized_products,
            'product_count': data['product_count'],
            'top_products': serialized_top
        }

    return serialized
