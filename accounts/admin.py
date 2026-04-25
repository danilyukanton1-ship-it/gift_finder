from django.contrib import admin

from .models import SavedSearch, SearchHistory, ChosenProducts


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
    ]
    search_fields = ['user']
    list_filter = ['options']
    ordering = ('-created_at',)


@admin.register(ChosenProducts)
class ChosenProductsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'product',
        'is_purchased',
    ]
    search_fields = ['user']
    list_filter = ['is_purchased']
    ordering = ('-selected_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'created_at',
    ]
    search_fields = ['user']
    ordering = ('-created_at',)
    filter_horizontal = ['options']
