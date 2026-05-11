from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from typing import Optional, Any, Dict, List, Tuple
from accounts.models import SearchHistory
from gifts.services.gift_search import (
    GiftSearchService,
    serialize_products_by_direction,
    DirectionData,
)


class DirectionViewService:

    def __init__(self, request: HttpRequest, option_ids: List[int]) -> None:
        self.request = request
        self.option_ids = option_ids
        self._result = None
        self._serializable_result = None

    def validate_options(self) -> Optional[HttpResponseRedirect]:
        """validation of chosen options, returns HttpResponseRedirect if not option_ids"""
        if not self.option_ids:
            messages.warning(self.request, "No options selected")
            return redirect("gifts:questionnaire")
        return None

    def save_search_history(self) -> None:
        """saves search history to session in user.is_authenticated"""
        if self.request.user.is_authenticated and self.option_ids:
            history = SearchHistory.objects.create(user=self.request.user)
            history.options.set(self.option_ids)

    def get_recommendations(self) -> Dict[int, DirectionData]:
        """Get recommendations from using GiftSearchService"""
        engine = GiftSearchService(self.option_ids)
        self._result = engine.get_result()
        return self._result

    def result_to_serializable(self) -> Dict[int, DirectionData]:
        """convert result into serializable dictionary"""
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
        return serializable_result

    def serialize_and_store_in_session(self) -> Dict[int, dict[str, Any]]:
        """serialize result and save into session"""
        if self._serializable_result is None:
            self._serializable_result = self.result_to_serializable()
        serialized = serialize_products_by_direction(self._serializable_result)
        self.request.session["all_products"] = serialized
        return serialized

    def prepare_directions_data(self) -> List[Dict[str, Any]]:
        """prepare directions data for showing in template"""
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

    def process_service(
        self,
    ) -> Tuple[Optional[HttpResponseRedirect], Optional[List[Dict[str, Any]]], bool]:
        """
        Returns:
            Tuple[HttpResponseRedirect | None, List[Dict] | None, bool]:
                - redirect_response: object of redirect or none
                - direction_data: data for template or none
                - should_render: flag, if we need to render template
        """
        redirect_response = self.validate_options()
        if redirect_response:
            return redirect_response, None, False

        self.save_search_history()
        self.serialize_and_store_in_session()

        direction_data = self.prepare_directions_data()

        return None, direction_data, True
