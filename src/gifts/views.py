from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView

from .models import Question, Tag, Product
from gifts.services.gift_search_services import (
    GiftSearchService,
    serialize_products_by_direction,
)
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from accounts.models import SearchHistory, Cart
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from gifts.services.question_view_services import (
    QuestionViewService,
)
from gifts.services.direction_view_services import (
    DirectionViewService,
)


class IndexView(TemplateView):
    template_name = "gifts/index.html"


class QuestionnaireView(View):
    template_name = "gifts/questionnaire.html"

    def get(self, request):
        questions = QuestionViewService.get_active_questions()
        context = {"questions": questions}
        return render(request, self.template_name, context)

    def post(self, request):
        questions = QuestionViewService.get_active_questions()
        selected_options = QuestionViewService.extract_selected(request.POST, questions)
        request.session["selected_options"] = selected_options
        return redirect("gifts:directions")


class DirectionView(View):
    template_name = "gifts/directions.html"

    def get(self, request):
        option_ids = request.session.get("selected_options", [])

        service = DirectionViewService(request, option_ids)
        redirect_response, direction_data, should_render = service.process_service()

        if redirect_response:
            return redirect_response

        return render(request, self.template_name, {"directions_data": direction_data})

class ProductView(View):
    template_name = "gifts/products.html"

    def get(self, request, direction_id):
        all_products = request.session.get("all_products", [])

        direction_data = all_products.get(str(direction_id), {})
        products = direction_data.get("products", [])

        if not products:
            messages.warning(request, "No products found in this direction.")
            return redirect("gifts:directions")

        context = {
            "products_data": products,
            "direction_id": direction_id,
            "direction_name": direction_data.get("direction_name"),
        }

        return render(request, self.template_name, context)


class CartView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"quantity": 1, "is_purchased": False},
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} quantity increased to {cart_item.quantity}')
        else:
            messages.success(request, f'{product.name} added to cart')

        return redirect(reverse("accounts:cart"))

@staff_member_required
def get_tags_by_question(request):
    question_id = request.GET.get("question_id")

    if not question_id:
        return JsonResponse({"error": "No question_id"}, status=400)

    # Все теги этого вопроса
    tags = Tag.objects.filter(question_id=question_id).values("id", "name")

    return JsonResponse({"tags": {tag["id"]: tag["name"] for tag in tags}})
