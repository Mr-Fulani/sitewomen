import unidecode
from django.contrib import admin, messages
from django.utils.text import slugify

from women.models import Women, Category, Husband


class MarriedFilter(admin.SimpleListFilter):
    title = 'Статус женщин'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('married', 'Замужем'),
            ('single', 'Не замужем'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'married':
            return queryset.filter(husband__isnull=False)
        elif self.value() == 'single':
            return queryset.filter(husband__isnull=True)


@admin.register(Women)
class WomenAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'content', 'cat', 'husband', 'tags') # поля "только для просмотра" при редактировании записи
    # exclude = ('tags', 'is_published') # поля исключенные при редактировании записи
    # readonly_fields = ('slug')
    prepopulated_fields = {'slug': ('title',)}
    # filter_horizontal = ('tags',)
    filter_vertical = ('tags',)
    list_display = ('title', 'time_create', 'is_published', 'cat', 'brief_info') # отображаемые поля
    list_display_links = ('title',) # кликабельные поля
    ordering = ('-time_create', 'title')
    list_editable = ('is_published',) # редактируемые поля
    list_per_page = 5
    actions = ('set_published', 'set_draft')
    search_fields = ('title', 'cat__name') # поиск (через панель поиска админки)
    list_filter = (MarriedFilter, 'cat__name', 'is_published')


    @admin.display(description="Краткое описание", ordering='content')
    def brief_info(self, women: Women) -> str:
        return f'Описание {len(women.content)} символов.'


    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Women.Status.PUBLISHED)
        self.message_user(request, f'Изменено {count} записей.')


    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Women.Status.DRAFT)
        self.message_user(request, f'{count} записей сняты с публикации.', messages.WARNING)

    def save(self, *args, **kwargs):
        transliterated_title = unidecode(self.title)
        self.slug = slugify(transliterated_title)
        super().save(*args, **kwargs)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')



@admin.register(Husband)
class HusbandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')