from django.contrib import admin
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme

from .models import ConsultationRequest, Order, PromoCode, SiteSettings


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_phone",
        "delivery_time",
        "status",
        "promo_code",
        "promo_discount",
        "total_price",
        "created_at",
        "paid_at",
    )
    list_display_links = ("id", "customer_name", "customer_phone")
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
        "promo_code",
        "promo_discount",
        "total_price",
        "created_at",
        "paid_at",
    )

    def response_change(self, request, obj):
        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return super().response_change(request, obj)


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "is_processed", "created_at")
    list_display_links = ("id", "customer_name", "phone")
    list_filter = ("is_processed", "created_at")
    search_fields = ("customer_name", "phone")
    list_editable = ("is_processed",)
    readonly_fields = ("created_at",)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_display",
        "min_order_sum",
        "used_count",
        "max_uses",
        "valid_until",
        "is_active",
    )
    list_filter = ("is_active", "discount_type")
    search_fields = ("code", "description")
    readonly_fields = ("used_count", "created_at")

    @admin.display(description="Скидка")
    def discount_display(self, obj):
        if obj.discount_type == PromoCode.DISCOUNT_PERCENT:
            return f"{obj.percent_off}%"
        return f"{obj.amount_off} ₽"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
