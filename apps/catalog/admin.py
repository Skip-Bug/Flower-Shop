from django.contrib import admin
from django.utils.html import format_html

from .models import Bouquet, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "image_preview", "is_active")
    list_display_links = ("title",)
    list_editable = ("is_active",)
    list_filter = ("events", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("events",)
    search_fields = ("title",)
    readonly_fields = ("image_preview",)

    @admin.display(description="Превью")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 5px;" />',
                obj.image.url,
            )
        return "Нет фото"

    fieldsets = (
        (
            "Основное",
            {"fields": ("title", "slug", "description", "composition", "size")},
        ),
        ("Цена и фото", {"fields": ("price", "image", "image_preview")}),
        ("События", {"fields": ("events",)}),
        ("Статус", {"fields": ("is_active",)}),
    )
