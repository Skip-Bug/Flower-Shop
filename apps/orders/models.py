from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.catalog.models import Bouquet

MONEY_QUANT = Decimal("0.01")


class PromoCode(models.Model):
    """Промокод для скидки при заказе."""

    DISCOUNT_PERCENT = "PERCENT"
    DISCOUNT_AMOUNT = "AMOUNT"

    code = models.CharField("Промокод", max_length=50, unique=True)
    discount_type = models.CharField(
        "Тип скидки",
        max_length=10,
        choices=[(DISCOUNT_PERCENT, "Процент"), (DISCOUNT_AMOUNT, "Сумма")],
        default=DISCOUNT_PERCENT,
    )
    percent_off = models.PositiveSmallIntegerField("Процент", default=0)
    amount_off = models.DecimalField(
        "Сумма скидки, р.",
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    min_order_sum = models.DecimalField(
        "Минимальная сумма заказа, р.",
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    max_uses = models.PositiveIntegerField(
        "Максимум применений",
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
    )
    used_count = models.PositiveIntegerField("Применено раз", default=0)
    valid_from = models.DateTimeField("Действует с", null=True, blank=True)
    valid_until = models.DateTimeField("Действует до", null=True, blank=True)
    is_active = models.BooleanField("Активен", default=True)
    description = models.CharField("Описание", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        ordering = ("-created_at",)

    def __str__(self):
        return self.code

    def clean(self):
        if self.discount_type == self.DISCOUNT_PERCENT:
            if not 1 <= self.percent_off <= 100:
                raise ValidationError(
                    {"percent_off": "Процент должен быть от 1 до 100"}
                )
        elif self.amount_off <= 0:
            raise ValidationError({"amount_off": "Укажите сумму скидки больше нуля"})

    @property
    def is_expired(self):
        return bool(self.valid_until and self.valid_until < timezone.now())

    @property
    def is_exhausted(self):
        return bool(self.max_uses and self.used_count >= self.max_uses)

    def is_usable_for(self, subtotal):
        if not self.is_active or self.is_expired or self.is_exhausted:
            return False
        if self.valid_from and self.valid_from > timezone.now():
            return False
        return subtotal >= self.min_order_sum

    def discount_for(self, subtotal):
        if not self.is_usable_for(subtotal):
            return Decimal("0")
        if self.discount_type == self.DISCOUNT_PERCENT:
            discount = subtotal * self.percent_off / Decimal("100")
            return discount.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
        return min(self.amount_off, subtotal)

    def reject_reason(self, subtotal):
        if not self.is_active:
            return "Промокод отключён"
        if self.is_expired:
            return "Срок действия промокода истёк"
        if self.valid_from and self.valid_from > timezone.now():
            return "Промокод ещё не действует"
        if self.is_exhausted:
            return "Промокод исчерпал лимит применений"
        if subtotal < self.min_order_sum:
            return f"Промокод действует от {self.min_order_sum:.0f} р."
        return ""


class Order(models.Model):
    STATUS_CHOICES = (
        ("new", "Новый (ожидает онлайн-оплаты)"),
        ("pending_cash", "Оплата при получении (нужно собрать)"),
        ("paid", "Оплачен (нужно собрать)"),
        ("assembling", "На сборке у флориста"),
        ("assembled", "Собран(ждет курьера)"),
        ("delivering", "У курьера (в пути)"),
        ("completed", "Выполнен (доставлен)"),
        ("canceled", "Отменен"),
    )

    class DeliveryTime(models.TextChoices):
        FAST = "fast", "Как можно скорее"
        T10_12 = "10_12", "с 10:00 до 12:00"
        T12_14 = "12_14", "с 12:00 до 14:00"
        T14_16 = "14_16", "с 14:00 до 16:00"
        T16_18 = "16_18", "с 16:00 до 18:00"
        T18_20 = "18_20", "с 18:00 до 20:00"

    class PaymentMethod(models.TextChoices):
        ONLINE = "online", "Онлайн (ЮKassa)"
        CASH = "cash", "При получении"

    customer_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон")
    delivery_address = models.TextField(verbose_name="Адрес доставки")
    delivery_time = models.CharField(
        max_length=20,
        choices=DeliveryTime.choices,
        default=DeliveryTime.FAST,
        verbose_name="Время доставки",
    )

    bouquet = models.ForeignKey(
        Bouquet, on_delete=models.SET_NULL, null=True, verbose_name="Букет"
    )

    bouquet_snapshot = models.JSONField(
        verbose_name="Данные букета на момент заказа", default=dict
    )

    bouquet_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Цена букета, р."
    )
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Доставка, р."
    )
    promo_discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Скидка, р."
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Итого, р."
    )
    promo = models.ForeignKey(
        PromoCode,
        verbose_name="Промокод",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    promo_code = models.CharField(
        "Промокод (текстом)", max_length=50, blank=True, default=""
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.ONLINE,
        verbose_name="Способ оплаты",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    paid_at = models.DateTimeField("Оплачен", null=True, blank=True)
    payment_id = models.CharField(
        "ID платежа ЮKassa",
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} - {self.customer_name}"


class ConsultationRequest(models.Model):
    customer_name = models.CharField("Имя клиента", max_length=100, blank=True)
    phone = models.CharField("Телефон", max_length=20)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    is_processed = models.BooleanField("Обработано", default=False)

    class Meta:
        verbose_name = "Заявка на консультацию"
        verbose_name_plural = "Заявки на консультации"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Консультация #{self.pk} - {self.customer_name or self.phone}"


class SiteSettings(models.Model):
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Стоимость доставки, р.",
    )

    class Meta:
        verbose_name = "Настройки магазина"
        verbose_name_plural = "Настройки магазина"

    def __str__(self):
        return "Глобальные настройки"
