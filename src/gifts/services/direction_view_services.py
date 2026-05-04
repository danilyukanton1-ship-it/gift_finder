from django.contrib import messages
from django.shortcuts import redirect

from accounts.models import SearchHistory
from gifts.services import GiftSearchService, serialize_products_by_direction


class DirectionViewService:

    def __init__(self, request, option_ids):
        self.request = request
        self.option_ids = option_ids
        self._result = None
        self._serializable_result = None

    def validate_options(self):
        if not self.option_ids:
            messages.warning(self.request, "No options selected")
            return redirect("gifts:questionnaire")
        return None

    def save_search_history(self):
        if self.request.user.is_authenticated:
            history = SearchHistory.objects.create(user=self.request.user)
            history.options.set(self.option_ids)

    def get_recommendations(self):
        if self._result is None:
            engine = GiftSearchService(self.option_ids)
            self._result = engine.get_result()
            # Отладка
            print(f"=== DEBUG ===")
            print(f"option_ids: {self.option_ids}")
            print(f"result keys: {list(self._result.keys())}")
            print(f"result data: {self._result}")
            for dir_id, data in self._result.items():
                print(f"Direction {dir_id}: {len(data.get('products', []))} products")
        return self._result

    def result_to_serializable(self):
        if self._result is None:
            self._result = self.get_recommendations()

        serializable_result = {}
        for direction_id, data in self._result.items():
            serializable_result[direction_id] = {
                "direction": data["direction"],
                "products": data["products"],
                "product_count": len(data["products"]),
                "top_products": data["top_products"],
            }
        self._serializable_result = serializable_result
        return serializable_result

    def serialize_and_store_in_session(self):
        if self._serializable_result is None:
            serializable_result = self.result_to_serializable()
        else:
            serializable_result = self._serializable_result
        serialized = serialize_products_by_direction(serializable_result)
        self.request.session["all_products"] = serialized
        return serialized

    def prepare_directions_data(self):
        if self._result is None:
            self._result = self.get_recommendations()

        directions_data = []
        for direction_id, data in self._result.items():
            directions_data.append(
                {
                    "direction": data["direction"],
                    "product_count": data["product_count"],
                    "top_products": data["top_products"],
                }
            )
        directions_data.sort(key=lambda x: x["product_count"], reverse=True)

        return directions_data

    def process_service(self):
        redirect_response = self.validate_options()
        if redirect_response:
            return redirect_response, None, False

        self.save_search_history()
        self.get_recommendations()
        self.result_to_serializable()
        self.serialize_and_store_in_session()

        direction_data = self.prepare_directions_data()

        return None, direction_data, True
