from django.db import models


class Event(models.Model):
    name = models.CharField("Название события", max_length=100)
    slug = models.SlugField("URL-идентификатор", unique=True)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

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
