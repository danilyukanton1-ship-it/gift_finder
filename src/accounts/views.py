from pyexpat.errors import messages

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChosenProducts, SearchHistory, SavedSearch


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')

    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        item = ChosenProducts.objects.get(id=item_id, user=request.user)
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
    return redirect('accounts:cart')


@login_required
def delete_from_cart(request, item_id):
    if request.method == 'POST':
        deleted, _ = ChosenProducts.objects.filter(id=item_id, user=request.user).delete()
        if deleted:
            messages.success(request, 'Item removed from cart.')
        else:
            messages.warning(request, 'Item not removed from cart.')
        return redirect('accounts:cart')

    return redirect('accounts:cart')


@login_required
def cart(request):
    cart_items = ChosenProducts.objects.filter(user=request.user, is_purchased=False).select_related('product')

    total = sum(item.quantity * item.product.price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'accounts/cart.html', context)


@login_required
def profile(request):
    search_history = SearchHistory.objects.filter(user=request.user).count()
    saved_search = SavedSearch.objects.filter(user=request.user).count()
    chosen_products = ChosenProducts.objects.filter(user=request.user).count()
    context = {
        'search_history': search_history,
        'saved_search': saved_search,
        'chosen_products': chosen_products,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def search_history(request):
    context = {
        'search_history': SearchHistory.objects.filter(user=request.user).prefetch_related('options').order_by('-created_at'),
    }
    return render(request, 'accounts/search_history.html', context)
