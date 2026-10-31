import random
from decimal import Decimal

from django.conf import settings
from django.urls import reverse
from yookassa import Configuration, Payment

from apps.catalog.models import Bouquet
from apps.orders.models import SiteSettings

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
        idempotence_key=f"order-{order.id}",
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

    return order
