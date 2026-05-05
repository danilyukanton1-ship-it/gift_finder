from pyexpat.errors import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.generic import TemplateView
from .models import Cart
from django.views import View
from accounts.selectors import (
    cart_items_get,
    cart_items_get_with_item_total,
    cart_total_price,
    search_history_get,
    saved_search_get,
)


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
        return render(request, self.template_name, {"form": form})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class UpdateCartView(LoginRequiredMixin, View):

    def post(self, request, item_id):
        quantity = int(request.POST.get("quantity", 1))
        item = get_object_or_404(Cart, id=item_id, user=request.user)
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
        return redirect("accounts:cart")


class DeleteFromCartView(LoginRequiredMixin, View):

    def post(self, request, item_id):
        deleted, _ = Cart.objects.filter(id=item_id, user=request.user).delete()
        if deleted:
            messages.success(request, "Item removed from cart.")
        else:
            messages.warning(request, "Item not removed from cart.")
        return redirect("accounts:cart")


class CartView(LoginRequiredMixin, View):
    template_name = "accounts/cart.html"

    def get(self, request):
        cart_items = cart_items_get_with_item_total(request)

        total = cart_total_price(cart_items)
        context = {
            "cart_items": cart_items,
            "total": total,
        }
        return render(request, self.template_name, context)


class CartCountView(LoginRequiredMixin, View):

    def get(self, request):
        count = cart_items_get(request).count()
        return JsonResponse({"count": count})


class ProfileViewContext(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        context = {
            "search_history": search_history_get(request=request).count(),
            "saved_search": saved_search_get(request=request).count(),
            "cart": cart_items_get(request=request).count(),
        }
        return render(request, self.template_name, context)


class SearchHistoryView(LoginRequiredMixin, View):
    template_name = "accounts/search_history.html"

    def get(self, request):
        context = {
            "search_history": search_history_get(request=request)
            .prefetch_related("options")
            .order_by("-created_at"),
        }
        return render(request, self.template_name, context)
