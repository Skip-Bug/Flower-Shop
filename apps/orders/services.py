import random
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from yookassa import Configuration, Payment

from apps.catalog.models import Bouquet
from apps.orders.models import Order, PromoCode, SiteSettings

BUDGET_PRICE_RANGES = {
    "low": (Decimal("0"), Decimal("1000")),
    "medium": (Decimal("1000"), Decimal("5000")),
    "high": (Decimal("5000"), None),
}


def pick_bouquet_for_quiz(occasion_slug, budget_key):
    if not occasion_slug or not budget_key:
        return None

    if budget_key != "any" and budget_key not in BUDGET_PRICE_RANGES:
        return None

    matched = Bouquet.objects.filter(
        is_active=True,
        events__slug=occasion_slug,
        events__is_active=True,
    )

    price_range = BUDGET_PRICE_RANGES.get(budget_key)
    if price_range:
        low, high = price_range
        matched = matched.filter(price__gte=low)
        if high is not None:
            matched = matched.filter(price__lt=high)

    count = matched.count()
    if count == 0:
        return None
    random_index = random.randint(0, count - 1)
    return matched[random_index]


def create_yookassa_payment(order, request):
    """Создает платеж в ЮKassa и возвращает объект payment."""
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    return_url = request.build_absolute_uri(
        reverse("orders:payment_success", kwargs={"order_id": order.id})
    )

    payment = Payment.create(
        {
            "amount": {"value": str(order.total_price), "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": f"Заказ №{order.id} - FlowerShop",
        },
        idempotency_key=f"order-{order.id}",
    )

    return payment


def build_bouquet_snapshot(bouquet):
    """Возвращает словарь с данными букета на момент заказа."""
    return {
        "id": bouquet.id,
        "title": bouquet.title,
        "slug": bouquet.slug,
        "price": str(bouquet.price),
        "description": bouquet.description,
        "composition": bouquet.composition,
        "size": bouquet.size,
        "image_url": bouquet.image.url if bouquet.image else None,
    }


def build_order_from_form(form, bouquet):
    """Создает объект заказа из формы несохраняя его в БД."""
    order = form.save(commit=False)
    order.bouquet = bouquet
    order.bouquet_snapshot = build_bouquet_snapshot(bouquet)

    settings_obj = SiteSettings.objects.get(id=1)
    order.bouquet_price = bouquet.price
    order.delivery_fee = settings_obj.delivery_fee
    order.total_price = bouquet.price + order.delivery_fee

    if order.payment_method == Order.PaymentMethod.CASH:
        order.status = "pending_cash"

    return order


def apply_promo(order, subtotal, code):
    """Начисляет скидку, если промокод применим. Возвращает текст ошибки.

    Вызывать только внутри transaction.atomic(): строка промокода блокируется
    через select_for_update, чтобы между проверкой лимита и инкрементом
    used_count не вклинился другой заказ.
    """
    if not code:
        return ""

    promo = PromoCode.objects.select_for_update().filter(code__iexact=code).first()
    if promo is None:
        return "Промокод не найден"

    discount = promo.discount_for(subtotal)
    if discount <= 0:
        return promo.reject_reason(subtotal)

    order.promo = promo
    order.promo_code = promo.code
    order.promo_discount = discount
    return ""


def place_order(form, order):
    """Сохраняет заказ и применяет промокод.

    Возвращает False, если промокод отклонён: заказ не сохраняется,
    а в форме появляется ошибка поля promo.
    """
    with transaction.atomic():
        promo_error = apply_promo(order, order.bouquet_price, form.get_promo())
        if promo_error:
            form.add_error("promo", promo_error)
            return False

        order.total_price = (
            order.bouquet_price + order.delivery_fee - order.promo_discount
        )
        order.save()

        if order.promo:
            PromoCode.objects.filter(pk=order.promo.pk).update(
                used_count=F("used_count") + 1
            )

    return True
