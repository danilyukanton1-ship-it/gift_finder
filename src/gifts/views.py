from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Question, Tag, Direction, Product
from .services import GiftSearchEngine, serialize_products_by_direction
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from accounts.models import SearchHistory, ChosenProducts
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def index(request):
    return render(request, "gifts/index.html")


def question_view(request):
    questions = Question.objects.filter(is_active=True).order_by("order")

    if request.method == "POST":
        selected_options = []
        for question in questions:
            answer_key = f"question_{question.id}"
            if answer_key in request.POST:
                value = request.POST.get(answer_key)
                if question.question_type == "multiple":
                    selected_options.extend(request.POST.getlist(answer_key))
                else:
                    selected_options.append(value)

        request.session["selected_options"] = selected_options

        return redirect("gifts:directions")
    return render(request, "gifts/questionnaire.html", {"questions": questions})


def direction_view(request):
    option_ids = request.session.get("selected_options", [])

    if not option_ids:
        messages.warning(request, "No option selected.")
        return redirect("gifts:questionnaire")

    if request.user.is_authenticated:
        history = SearchHistory.objects.create(user=request.user)
        history.options.set(option_ids)

    engine = GiftSearchEngine(option_ids)
    result = engine.get_result()

    # Преобразуем result в формат, который ожидает сериализатор
    result_for_serializer = {}
    for direction, data in result.items():
        result_for_serializer[direction.id] = {
            "direction": direction,
            "products": data["products"],
            "product_count": data["product_count"],
            "top_products": data["top_products"],
        }

    # ✅ Теперь сериализуем
    serialized_result = serialize_products_by_direction(result_for_serializer)
    request.session["all_products"] = serialized_result

    # Подготавливаем данные для шаблона (оставляем объекты)
    directions_data = []
    for direction, data in result.items():
        directions_data.append(
            {
                "direction": direction,
                "products_count": data["product_count"],
                "top_products": data["top_products"],
            }
        )

    directions_data.sort(key=lambda x: x["products_count"], reverse=True)

    return render(
        request, "gifts/directions.html", {"directions_data": directions_data}
    )


def product_view(request, direction_id):
    # Берём все товары из сессии
    all_products = request.session.get("all_products", {})

    # Ключ может быть строкой, приводим к строке для надёжности
    direction_data = all_products.get(str(direction_id), {})
    products = direction_data.get("products", [])

    if not products:
        messages.warning(request, "No products found in this direction.")
        return redirect("gifts:directions")

    context = {
        "products_data": products[:20],
        "direction_id": direction_id,
        "direction_name": direction_data.get("direction_name"),
    }
    return render(request, "gifts/products.html", context)


@login_required
def selected_products(request, product_id):
    """
    :param request:
    :param product_id:
    :return: add products to the cart
    """
    print("functions is working!!!!!!!!!!!!!!!!!")
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product does not exist."}, status=404)
    print(f"{product.id} - {product.name}")
    chosen, created = ChosenProducts.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 1, "is_purchased": False},
    )

    if not created:
        # Если товар уже есть — увеличиваем количество
        chosen.quantity += 1
        chosen.save()

    # ВСЕГДА редирект на корзину (или можно на страницу товаров)
    return redirect(reverse("accounts:cart"))


@staff_member_required
def get_tags_by_question(request):
    question_id = request.GET.get("question_id")

    if not question_id:
        return JsonResponse({"error": "No question_id"}, status=400)

    # Все теги этого вопроса
    tags = Tag.objects.filter(question_id=question_id).values("id", "name")

    return JsonResponse({"tags": {tag["id"]: tag["name"] for tag in tags}})
