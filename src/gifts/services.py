from gifts.selectors import (
    options_fetch,
    question_get_by_order,
    products_all_with_tags_and_directions,
)


class UserTagService:
    def __init__(self, options):
        self.options = options_fetch(options)
        self.tags_by_questions = self._build_tags_by_question()

    def _build_tags_by_question(self):
        """Build mapping from question to set of tags"""
        tags_from_options = {}

        for option in self.options:
            question = option.question
            tags = set(question.tags.all())
            if question in tags_from_options:
                tags_from_options[question] |= tags
            else:
                tags_from_options[question] = tags

        return tags_from_options

    def get_tags_for_questions(self, question):
        """Get user selected tags for a specific question"""
        return self.tags_by_questions.get(question, set())

    def get_all_questions(self):
        """Get all questions that user answered"""
        return self.tags_by_questions.keys()

    def calculate_max_score(self):
        """Calculate max possible score that product can receive if matching all the tags"""
        max_score = 0
        for question, tags in self.tags_by_questions.items():
            max_score += len(tags) * question.priority
        return max_score

    def get_all_user_tags(self):
        """Get all tags selected by user across all questions"""
        all_tags = set()
        for tags in self.tags_by_questions.values():
            all_tags.update(tags)
        return all_tags


class ProductScoreService:

    def __init__(self, user_tags_service):
        self._user_tag_service = user_tags_service

    def calculate_product_score(self, product_tags):
        """Calculate product score based on weighted tag matches"""
        product_score = 0
        questions = self._user_tag_service.all_questions()
        for question in questions:
            product_question_tags = {
                tag for tag in product_tags if tag.question == question
            }
            user_question_tags = self._user_tag_service.get_tags(question)
            match = product_question_tags.intersection(user_question_tags)
            score = len(match) * question.priority
            product_score += score
        return product_score

    def calculate_normalized_score(self, product_tags):
        """Calculate normalized score (0-100) for a product"""
        product_score = self.calculate_product_score(product_tags)
        max_score = self._user_tag_service.calculate_max_score()
        if max_score == 0:
            return 0
        return (product_score / max_score) * 100


class ProductFilterService:

    SCORE_NEEDED = 40

    def __init__(self, user_tags_service, question_order_1, question_order_6):
        self.user_tags_service = user_tags_service
        self.question_order_1 = question_order_1
        self.question_order_6 = question_order_6
        self.score_calculator = ProductScoreService(user_tags_service)

    def validate_by_recipient(self, product_tags):
        """Checks if product has tags matching the recipient tags of a user"""
        user_tags = self.user_tags_service.get_tags(self.question_order_1)
        product_tags_filtered = {
            tag for tag in product_tags if tag.question == self.question_order_1
        }
        return bool(user_tags & product_tags_filtered)

    def validate_by_hobby(self, product_tags):
        """Checks if product has tags matching the hobby tags of a user"""
        user_tags = self.user_tags_service.get_tags(self.question_order_6)
        product_tags_filtered = {
            tag for tag in product_tags if tag.question == self.question_order_6
        }
        return bool(user_tags & product_tags_filtered)

    def score_validation(self, product_tags):
        """Checks if product's normalized score matches NEEDED score"""
        return self.score_calculator.calculate_normalized_score(product_tags) > self.SCORE_NEEDED

    def evaluate_product(self, product_tags):
        """
        Checks if product should be kept
        return: tuple(False or True, normalized score)
        """
        if not self.validate_by_recipient(product_tags):
            return False
        if not self.validate_by_hobby(product_tags):
            return False
        if not self.score_validation(product_tags):
            return False
        score = self.score_calculator.calculate_normalized_score(product_tags)

        return True, score


class ProductGroupService:

    def __init__(self, collected_products):
        self.collected_products = collected_products
        self.directions_grouped = self._group_by_direction()

    def _group_by_direction(self):
        """Group products by their direction"""
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

    def sort_by_score_in_directions(self):
        """Sort products by their score in their directions"""
        for data in self.directions_grouped.values():
            data["products"].sort(key=lambda item: item["weight_score"], reverse=True)
        return self

    def select_top_products(self, limit=3):
        """Select top (limit=N) products by their score in their directions"""
        for data in self.directions_grouped.values():
            data["top_products"] = data["products"][:limit]
        return self

    def get_grouped_result(self):
        """Return products grouped with top selections"""
        return self.directions_grouped


class GiftSearchService:

    REQUIRED_QUESTION_ORDERS = [1, 4, 5, 6, 7, 8, 9, 10]

    def __init__(self, options_ids):
        self.options = options_fetch(options_ids)
        self.question_order_1 = question_get_by_order(order=1)
        self.question_order_6 = question_get_by_order(order=6)
        self.all_products = products_all_with_tags_and_directions()

        self.user_tags_service = UserTagService(self.options)
        self.product_filter = ProductFilterService(
            self.user_tags_service,
            self.question_order_1,
            self.question_order_6,
        )

        self.collected_products = self._collect_products()
        self.product_grouper = ProductGroupService(self.collected_products)
        self.product_grouper.sort_by_score_in_directions().select_top_products(limit=3)
        self.directions_grouped = self.product_grouper.get_grouped_result()

    def has_answered_required(self):
        """Check if user answered all required questions"""
        orders = [option.question.order for option in self.options]
        for answer in self.REQUIRED_QUESTION_ORDERS:
            if answer not in orders:
                return False
        return True

    def _get_matched_tags(self, product_tags):
        """Get names of tags matching the product_tags"""
        all_user_tags = set()
        for tags in self.user_tags_service.tags_by_questions.values():
            all_user_tags.update(tags)
        matched_tags = all_user_tags.intersection(product_tags)
        return [tag.name for tag in matched_tags]

    def _collect_products(self):
        """Collecting products with all validators, filters, and scoring calculations
           Main orchestrator def
        """
        collected_products = []
        for product in self.all_products:
            product_tags = list(product.tags.all())
            should_keep, score = self.product_filter.evaluate_product(product_tags)
            if not should_keep:
                continue
            collected_products.append(
                {
                    "product": product,
                    "weight_score": score,
                    "matched_tags": self._get_matched_tags(product_tags),
                }
            )
        return collected_products

    def get_result(self):
        """return final results grouped by direction"""
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
