from .models import Option, Product, Question
from gifts.selectors import (
    options_get_from_options_ids,
    question_get_by_order,
)

class GiftSearchEngine:

    def __init__(self, options_ids):
        self.required_answers = [1, 4, 5, 6, 7, 8, 9, 10]
        self.options = options_get_from_options_ids(options_ids)
        self.tags_by_questions = self.tags_get_from_options()
        self.question_order_1 = question_get_by_order(order=1)
        self.question_order_6 = question_get_by_order(order=6)
        self.collected_products = self._collect_products()
        self.directions_grouped = self._group_products_by_direction()
        self._sort_in_directions()
        self._prepare_top_products(limit=3)

    def tags_get_from_options(self):
        tags_from_options = {}

        for option in self.options:
            question = option.question
            tags = set(question.tags.all())
            if question in tags_from_options:
                tags_from_options[question] |= tags
            else:
                tags_from_options[question] = tags

        return tags_from_options


    def has_required_answer(self):
        """check if the user answered all the required questions"""
        orders = [option.question.order for option in self.options]
        for answer in self.required_answers:
            if answer not in orders:
                return False
        return True

    def _validate_product_by_recipient(self, product):
        """check if product has tags associated with recipient the user have chosen"""
        product_tags = set(product.tags.filter(question=self.question_order_1))
        if not (self.tags_by_questions[self.question_order_1] & product_tags):
            return False
        return True

    def _validate_product_by_hobby(self, product):
        """check if product has tags associated with hobby the user have chosen"""
        product_tags = set(product.tags.filter(question=self.question_order_6))
        if not (self.tags_by_questions[self.question_order_6] & product_tags):
            return False
        return True

    def _calculate_max_score(self):
        max_score = 0
        for question, user_tags in self.tags_by_questions.items():
            max_score += len(user_tags) * question.priority
        return max_score

    def _calculate_product_score(self, product):
        product_score = 0
        questions = self.tags_by_questions.keys()
        for question in questions:
            product_question_tags = set(product.tags.filter(question=question))
            user_question_tags = self.tags_by_questions[question]
            match = product_question_tags.intersection(user_question_tags)
            score = len(match) * question.priority
            product_score += score
        return product_score

    def _get_matched_tags(self, product):
        all_user_tags = set()
        for tags in self.tags_by_questions.values():
            all_user_tags.update(tags)
        product_tags_names = (tag.name for tag in product.tags.all())
        matched = all_user_tags.intersection(product_tags_names)
        return list(matched)

    def _normalize_score(self, product):
        product_score = self._calculate_product_score(product)
        max_score = self._calculate_max_score()
        if max_score == 0:
            return 0
        result_score = (product_score / max_score) * 100
        return result_score

    def _score_validation(self, product):
        return self._normalize_score(product) > 40

    def _collect_products(self):
        collected_products = []
        products = (
            Product.objects.all().prefetch_related("tags").select_related("direction")
        )
        for product in products:
            if not self._validate_product_by_recipient(product):
                continue
            if not self._validate_product_by_hobby(product):
                continue
            if not self._score_validation(product):
                continue
            collected_products.append(
                {
                    "product": product,
                    "weight_score": self._normalize_score(product),
                    "matched_tags": self._get_matched_tags(product),
                }
            )

        return collected_products

    def _group_products_by_direction(self):
        directions_grouped = {}
        for product in self.collected_products:
            direction = product["product"].direction
            if direction not in directions_grouped:
                directions_grouped[direction] = {
                    "direction": direction,
                    "products": [],
                    "product_count": 0,
                    "top_products": [],
                }
            directions_grouped[direction]["products"].append(product)
            directions_grouped[direction]["product_count"] += 1
        return directions_grouped

    def _sort_in_directions(self):
        for data in self.directions_grouped.values():
            data["products"].sort(key=lambda item: item["weight_score"], reverse=True)

    def _prepare_top_products(self, limit=3):
        for data in self.directions_grouped.values():
            data["top_products"] = data["products"][:limit]

    def get_result(self):
        return self.directions_grouped


def serialize_products_by_direction(products_by_direction):
    """
    :param products_by_direction:
    :return: serializable list of dirs of products
    """
    serialized = {}
    for dir_id, data in products_by_direction.items():
        serialized_products = []
        for product_data in data["products"]:
            serialized_products.append(
                {
                    "product_id": product_data["product"].id,
                    "product_name": product_data["product"].name,
                    "product_price": float(product_data["product"].price),
                    "product_currency": product_data["product"].currency,
                    "product_source": product_data["product"].source,
                    "product_url": product_data["product"].product_url,
                    "product_image_url": product_data["product"].image_url,
                    "product_rating": (
                        float(product_data["product"].rating)
                        if product_data["product"].rating
                        else None
                    ),
                    "weight_score": product_data["weight_score"],
                }
            )

        serialized_top = []
        for product_data in data["top_products"]:
            serialized_top.append(
                {
                    "product_id": product_data["product"].id,
                    "product_name": product_data["product"].name,
                    "product_price": float(product_data["product"].price),
                    "product_currency": product_data["product"].currency,
                    "product_source": product_data["product"].source,
                    "product_url": product_data["product"].product_url,
                    "product_image_url": product_data["product"].image_url,
                    "product_rating": (
                        float(product_data["product"].rating)
                        if product_data["product"].rating
                        else None
                    ),
                    "weight_score": product_data["weight_score"],
                }
            )

        serialized[dir_id] = {
            "direction_id": data["direction"].id,
            "direction_name": data["direction"].name,
            "products": serialized_products,
            "product_count": data["product_count"],
            "top_products": serialized_top,
        }

    return serialized
