from django.core.exceptions import ValidationError
from django.db import models

from apps.common.phone import format_phone_national, normalize_phone


class Event(models.Model):
    name = models.CharField("Название события", max_length=100)
    slug = models.SlugField("URL-идентификатор", unique=True)
    is_active = models.BooleanField("Активно", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Bouquet(models.Model):
    title = models.CharField(
        "Название",
        max_length=200,
    )
    slug = models.SlugField("URL-идентификатор", max_length=200, unique=True)

    events = models.ManyToManyField(
        Event, blank=True, related_name="bouquets", verbose_name="События"
    )

    description = models.TextField("Описание и смысл букета", blank=True)
    composition = models.TextField("Состав", blank=True)
    size = models.CharField("Размер", max_length=100, blank=True)

    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField(
        "Фото",
        upload_to="bouquets/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Букет"
        verbose_name_plural = "Букеты"
        ordering = ["-id"]

    def __str__(self):
        return self.title


class Store(models.Model):
    address = models.CharField("Адрес", max_length=200)
    phone = models.CharField("Телефон", max_length=20)
    is_active = models.BooleanField("Активен", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Адрес магазина"
        verbose_name_plural = "Адреса магазинов"
        ordering = ["order", "address"]

    def __str__(self):
        return self.address

    def clean(self):
        super().clean()
        normalized = normalize_phone(self.phone)
        if normalized is None:
            raise ValidationError({"phone": "Некорректный номер телефона"})
        self.phone = normalized

    @property
    def phone_display(self):
        return format_phone_national(self.phone)

    @property
    def phone_link(self):
        return normalize_phone(self.phone) or self.phone
