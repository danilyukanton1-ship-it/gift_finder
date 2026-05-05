from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

app_name = "accounts"

urlpatterns = [
    path("search-history/", views.SearchHistoryView.as_view(), name="search_history"),
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
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path(
        "cart/update/<int:item_id>/", views.UpdateCartView.as_view(), name="update_cart"
    ),
    path(
        "cart/delete/<int:item_id>/",
        views.DeleteFromCartView.as_view(),
        name="delete_from_cart",
    ),
    path("cart/count/", views.CartCountView.as_view(), name="cart_count"),
]
