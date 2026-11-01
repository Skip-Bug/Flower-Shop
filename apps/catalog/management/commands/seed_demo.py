from decimal import Decimal

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Bouquet, Event


class Command(BaseCommand):
    help = "Заполняет базу демо-событиями, букетами и скачивает фото"

    def handle(self, *args, **options):
        self.stdout.write("Начинаем заполнение демо-данных...")
        events = self.create_events()
        self.create_bouquets(events)
        self.stdout.write(
            self.style.SUCCESS("Готово! Демо-данные (9 букетов) и фото загружены.")
        )

    def create_events(self):
        events_data = [
            ("День рождения", "birthday", 1),
            ("Свадьба", "wedding", 2),
            ("Без повода", "just-because", 3),
            ("Корпоратив", "corporate", 4),
        ]
        events = {}
        for name, slug, order in events_data:
            event, created = Event.objects.get_or_create(
                slug=slug, defaults={"name": name, "order": order, "is_active": True}
            )
            events[slug] = event
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создано событие: {event.name}"))
        return events

    def create_bouquets(self, events):
        bouquets_data = [
            {
                "title": "Нежность",
                "slug": "nezhnost",
                "price": Decimal("3500.00"),
                "description": "Легкий и воздушный букет для самого близкого человека.",
                "composition": "Пионы, эустома, гортензия",
                "size": "Средний",
                "events": ["birthday", "just-because"],
                "image_url": "https://images.unsplash.com/photo-1563241527-3004b7be0ffd?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Страсть",
                "slug": "strast",
                "price": Decimal("5800.00"),
                "description": "Яркий и страстный букет для признания в любви или годовщины.",
                "composition": "Красные розы 51 шт, рускус",
                "size": "Большой",
                "events": ["birthday", "wedding"],
                "image_url": "https://images.unsplash.com/photo-1490750967868-88cb4ecb07e0?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Весеннее настроение",
                "slug": "spring-mood",
                "price": Decimal("2500.00"),
                "description": "Свежий весенний букет из тюльпанов, который поднимет настроение кому угодно.",
                "composition": "Тюльпаны 15 шт, зелень",
                "size": "Средний",
                "events": ["birthday", "just-because"],
                "image_url": "https://images.unsplash.com/photo-1520763185298-1b434c919102?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Бизнес-леди",
                "slug": "business-lady",
                "price": Decimal("7200.00"),
                "description": "Строгий, но элегантный букет для делового партнера или руководителя.",
                "composition": "Белые розы, орхидеи, сухоцветы",
                "size": "Большой",
                "events": ["corporate"],
                "image_url": "https://images.unsplash.com/photo-1591886976077-9e32105b687f?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Бюджетный вариант",
                "slug": "budget",
                "price": Decimal("900.00"),
                "description": "Милый и аккуратный букетик, чтобы просто порадовать.",
                "composition": "Хризантемы, герберы",
                "size": "Маленький",
                "events": ["just-because", "birthday"],
                "image_url": "https://images.unsplash.com/photo-1596079890744-c1a0462d0975?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Солнечный день",
                "slug": "sunny-day",
                "price": Decimal("3200.00"),
                "description": "Яркий букет из подсолнухов, который подарит улыбку даже в пасмурный день.",
                "composition": "Подсолнухи 7 шт, солидаго",
                "size": "Средний",
                "events": ["birthday", "just-because"],
                "image_url": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Розовый рассвет",
                "slug": "pink-dawn",
                "price": Decimal("4500.00"),
                "description": "Нежный и романтичный букет в пастельных тонах. Идеален для невест.",
                "composition": "Розы, эустома, бруния",
                "size": "Средний",
                "events": ["wedding"],
                "image_url": "https://images.unsplash.com/photo-1561181286-d3fee7d55364?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Мужской характер",
                "slug": "mens-character",
                "price": Decimal("6500.00"),
                "description": "Сдержанный, стильный букет с темными акцентами. Отличный вариант для коллег.",
                "composition": "Розы, сухоцветы, эвкалипт",
                "size": "Большой",
                "events": ["corporate"],
                "image_url": "https://images.unsplash.com/photo-1508610048659-a06b669e3321?q=80&w=800&auto=format&fit=crop",
            },
            {
                "title": "Минимализм",
                "slug": "minimalism",
                "price": Decimal("800.00"),
                "description": "Один цветок, но какой! Для тех, кто ценит лаконичность.",
                "composition": "1 крупная гербера, зелень",
                "size": "Маленький",
                "events": ["just-because"],
                "image_url": "https://images.unsplash.com/photo-1599731990321-49b8605ee32e?q=80&w=800&auto=format&fit=crop",
            },
        ]

        for data in bouquets_data:
            event_slugs = data.pop("events")
            image_url = data.pop("image_url")

            bouquet, created = Bouquet.objects.get_or_create(
                slug=data["slug"], defaults=data
            )

            if not created:
                continue

            for slug in event_slugs:
                bouquet.events.add(events[slug])

            self.download_image(bouquet, image_url)
            self.stdout.write(self.style.SUCCESS(f"Создан букет: {bouquet.title}"))

    def download_image(self, bouquet, image_url):
        if not image_url:
            return

        self.stdout.write(f"  Загрузка фото для '{bouquet.title}'...")
        try:
            response = requests.get(image_url, timeout=15)
            if response.status_code == 200:
                file_name = f"{bouquet.slug}.jpg"
                bouquet.image.save(file_name, ContentFile(response.content), save=True)
            else:
                self.stderr.write(
                    self.style.WARNING(
                        f"  Не удалось скачать (код {response.status_code})"
                    )
                )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  Ошибка при скачивании фото: {e}"))
