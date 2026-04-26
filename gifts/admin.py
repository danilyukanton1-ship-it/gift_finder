from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Question, Tag, Option, Direction, Product
from django.contrib.admin import SimpleListFilter
from django import forms


# filters and other logic
class QuestionTagFilter(SimpleListFilter):
    title = 'Tag filter on question'
    parameter_name = 'tag_question'

    def lookups(self, request, model_admin):
        questions = Question.objects.filter(tags__isnull=False).distinct()
        return [(q.id, q.text) for q in questions]

    def queryset(self, request, queryset):
        return queryset


class ProductAdminForm(forms.ModelForm):
    tag_question = forms.ModelChoiceField(
        queryset=Question.objects.filter(tags__isnull=False).distinct(),
        required=False,
        label='Show tags from question'
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически добавляем поля для тегов
        if self.data:
            # При POST-запросе добавляем поля для всех возможных тегов
            for key in self.data:
                if key.startswith('tag_') and key != 'tag_question':
                    field_name = key
                    self.fields[field_name] = forms.BooleanField(
                        required=False,
                        initial=True
                    )

        # Загружаем выбранные теги для отображения
        self.selected_tag_ids = []
        if self.instance.pk:
            self.selected_tag_ids = list(self.instance.tags.values_list('id', flat=True))

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Собираем теги из данных формы
            tag_ids = []
            for key, value in self.cleaned_data.items():
                if key.startswith('tag_') and key != 'tag_question' and value:
                    try:
                        tag_id = int(key.replace('tag_', ''))
                        tag_ids.append(tag_id)
                    except ValueError:
                        pass

            # Сохраняем теги
            if tag_ids:
                instance.tags.set(tag_ids)
            else:
                instance.tags.clear()

        return instance


# registration
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type', 'priority', 'order', 'is_active']
    list_filter = ['question_type', 'is_active', 'priority']
    search_fields = ['text']
    list_editable = ['priority']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'question_link']
    search_fields = ['name']
    list_filter = ['question']
    autocomplete_fields = ['question']

    def question_link(self, obj):
        if obj.question:
            url = reverse('admin:gifts_question_change', args=(obj.question.id,))
            return mark_safe(f'<a href="{url}">{obj.question.text}</a>')
        return '-'

    question_link.short_description = 'Question'


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'order', 'is_active']
    list_filter = ['question', 'is_active']
    search_fields = ['text']
    filter_horizontal = ['tags']


if not admin.site.is_registered(Direction):
    @admin.register(Direction)
    class DirectionAdmin(admin.ModelAdmin):
        list_display = ['name', 'parent', 'order']
        list_filter = ['parent']
        search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'currency', 'source', 'rating']
    list_filter = ['source', 'currency', 'in_stock']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'last_checked']

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = ProductAdminForm
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Main information', {
                'fields': ['name', 'direction', 'in_stock']
            }),
            ('Price', {
                'fields': ['price', 'currency']
            }),
            ('Source', {
                'fields': ['source', 'product_url', 'image_url']
            }),
            ('Rating and description', {
                'fields': ['rating', 'description']
            }),
            ('Tag filter', {
                'fields': ['tag_question'],
                'classes': ['wide']
            }),
            ('System information', {
                'fields': ['created_at', 'last_checked'],
                'classes': ['collapse']
            }),
        ]
        return fieldsets

    def render_change_form(self, request, context, *args, **kwargs):
        context['questions'] = Question.objects.filter(is_active=True).order_by('order')
        return super().render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        # Сначала сохраняем сам объект
        super().save_model(request, obj, form, change)

        # Собираем теги из POST
        tag_ids = []
        for key, value in request.POST.items():
            if key.startswith('tag_') and key != 'tag_question' and value == '1':
                try:
                    tag_id = int(key.replace('tag_', ''))
                    tag_ids.append(tag_id)
                except ValueError:
                    pass

        # Сохраняем теги
        if tag_ids:
            obj.tags.set(tag_ids)
        else:
            obj.tags.clear()
