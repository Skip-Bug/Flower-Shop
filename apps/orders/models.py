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

    customer_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон")
    delivery_address = models.TextField(verbose_name="Адрес доставки")
    delivery_time = models.CharField(max_length=100, verbose_name="Время доставки")

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

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} - {self.customer_name}"
