from django.urls import path

from . import views

app_name = "gifts"

urlpatterns = [
    path("welcome", views.index, name="welcome"),
    path("", views.question_view, name="questionnaire"),
    path("directions/", views.direction_view, name="directions"),
    path("products/<int:direction_id>/", views.product_view, name="products"),
    path(
        "ajax/get-tags-by-question/",
        views.get_tags_by_question,
        name="get_tags_by_question",
    ),
    path(
        "products/<int:product_id>/select",
        views.selected_products,
        name="selected_products",
    ),
]
