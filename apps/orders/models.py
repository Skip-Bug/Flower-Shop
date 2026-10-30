from django.db import models

from apps.catalog.models import Bouquet


class Order(models.Model):
    STATUS_CHOICES = (
        ("new", "Новый (ожидает оплаты)"),
        ("paid", "Оплачен (нужно собрать)"),
        ("assembling", "На сборке у флориста"),
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
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Итого, р."
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    paid_at = models.DateTimeField("Оплачен", null=True, blank=True)

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
