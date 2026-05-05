from accounts.models import Cart, SearchHistory, SavedSearch
from django.db.models import Sum, F
import decimal

def cart_items_get_with_item_total(request):
    cart_items = (
        Cart.objects.filter(user=request.user, is_purchased=False)
        .select_related("product")
        .annotate(item_total=F("quantity") * F("product__price"))
    )
    return cart_items

def cart_total_price(cart_items):
    total = cart_items.aggregate(Sum("item_total"))["item_total__sum"] or decimal.Decimal(0)
    return total

def search_history_get(request):
    search_history = SearchHistory.objects.filter(user=request.user)
    return search_history

def saved_search_get(request):
    saved_search = SavedSearch.objects.filter(user=request.user)
    return saved_search

def cart_items_get(request):
    cart_count = Cart.objects.filter(user=request.user, is_purchased=False)
    return cart_count