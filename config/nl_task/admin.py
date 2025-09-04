from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Q
from .models import Page, Video, Audio, Text, PageContent
from django.contrib.contenttypes.models import ContentType

# Кастомная форма для PageContent
class PageContentForm(forms.ModelForm):
    content_object_id = forms.ChoiceField(label="Контент")
    
    class Meta:
        model = PageContent
        fields = ('content_object_id', 'order')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Формируем список доступного контента
        content_choices = []
        for model in [Video, Audio, Text]:
            content_type = ContentType.objects.get_for_model(model)
            for obj in model.objects.all():
                value = f"{content_type.id}_{obj.id}"
                label = f"{obj.title} ({model.__name__})"
                content_choices.append((value, label))
        
        self.fields['content_object_id'].choices = content_choices
        
        # Устанавливаем初始值 для редактирования
        if self.instance and self.instance.content_object:
            content_type = ContentType.objects.get_for_model(self.instance.content_object.__class__)
            self.initial['content_object_id'] = f"{content_type.id}_{self.instance.object_id}"

    def save(self, commit=True):
        # Извлекаем content_type и object_id из выбранного значения
        content_type_id, object_id = self.cleaned_data['content_object_id'].split('_')
        self.instance.content_type_id = int(content_type_id)
        self.instance.object_id = int(object_id)
        return super().save(commit)

# Inline для управления контентом на странице
class PageContentInline(admin.TabularInline):
    model = PageContent
    form = PageContentForm
    extra = 1
    verbose_name = "Элемент контента"
    verbose_name_plural = "Элементы контента"

# Фильтр для поиска по заголовку (начало строки)
class TitleSearchFilter(admin.SimpleListFilter):
    title = 'Заголовок'
    parameter_name = 'title'

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(title__istartswith=self.value())
        return queryset

# Страница в админке
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = (TitleSearchFilter,)
    search_fields = ('title',)
    inlines = [PageContentInline]

    def get_search_results(self, request, queryset, search_term):
        # Поиск по частичному совпадению от начала
        if search_term:
            queryset = queryset.filter(title__istartswith=search_term)
        return queryset, False

# Базовый класс для контента
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'counter', 'content_type')
    list_filter = (TitleSearchFilter,)
    search_fields = ('title',)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(title__istartswith=search_term)
        return queryset, False

# Регистрация моделей контента
admin.site.register(Video, ContentAdmin)
admin.site.register(Audio, ContentAdmin)
admin.site.register(Text, ContentAdmin)