from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    readonly_fields = (
        "bouquet_snapshot",
        "bouquet_price",
        "delivery_fee",
        "total_price",
        "created_at",
    )
