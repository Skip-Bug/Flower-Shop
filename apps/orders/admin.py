from django.contrib import admin

from .models import ConsultationRequest, Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_phone",
        "delivery_time",
        "status",
        "total_price",
        "created_at",
        "paid_at",
    )
    list_filter = ("status", "delivery_time", "created_at", "paid_at")
    search_fields = (
        "customer_name",
        "customer_phone",
        "delivery_address",
        "bouquet__title",
    )
    list_editable = ("status",)
    readonly_fields = (
        "bouquet_snapshot",
        "bouquet_price",
        "delivery_fee",
        "total_price",
        "created_at",
        "paid_at",
    )


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "is_processed", "created_at")
    list_filter = ("is_processed", "created_at")
    search_fields = ("customer_name", "phone")
    list_editable = ("is_processed",)
    readonly_fields = ("created_at",)
