from django.contrib import admin

from apps.catalog.models import Bouquet, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "is_active")
    list_filter = ("events", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("events",)
    search_fields = ("title",)
