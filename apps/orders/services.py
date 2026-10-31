import random
from decimal import Decimal

from apps.catalog.models import Bouquet

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
