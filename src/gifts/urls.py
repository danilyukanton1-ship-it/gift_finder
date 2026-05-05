from django.urls import path

from . import views

app_name = "gifts"

urlpatterns = [
    path("welcome", views.IndexView.as_view(), name="welcome"),
    path("", views.QuestionnaireView.as_view(), name="questionnaire"),
    path("directions/", views.DirectionView.as_view(), name="directions"),
    path("products/<int:direction_id>/", views.ProductView.as_view(), name="products"),
    path(
        "ajax/get-tags-by-question/",
        views.get_tags_by_question,
        name="get_tags_by_question",
    ),
    path(
        "products/<int:product_id>/select",
        views.CartView.as_view(),
        name="selected_products",
    ),
]
