from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("search-history/", views.search_history, name="search_history"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="gifts:questionnaire"),
        name="logout",
    ),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("cart/", views.cart, name="cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path("cart/delete/<int:item_id>/", views.delete_from_cart, name="delete_from_cart"),
    path("cart/count/", views.cart_count, name="cart_count"),
]
