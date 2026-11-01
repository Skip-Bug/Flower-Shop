from decimal import Decimal

import requests
import urllib3
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Bouquet, Event

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        for data in self.get_bouquets_data():
            self.process_bouquet(data, events)

    def process_bouquet(self, data, events):
        event_slugs = data.pop("events")
        image_query = data.pop("image_query")

        bouquet, created = Bouquet.objects.get_or_create(
            slug=data["slug"], defaults=data
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Создан букет: {bouquet.title}"))
            for slug in event_slugs:
                bouquet.events.add(events[slug])
        else:
            self.stdout.write(f"Букет {bouquet.title} уже есть в базе.")

        if not bouquet.image and image_query:
            self.attach_image(bouquet, image_query)

    def attach_image(self, bouquet, image_query):
        self.stdout.write(
            f"  Поиск фото для '{bouquet.title}' по запросу '{image_query}'..."
        )
        image_url = self.search_commons_image(image_query)

        if not image_url:
            self.stderr.write(
                self.style.WARNING(f"  Не удалось найти фото по запросу {image_query}")
            )
            return

        self.download_image(bouquet, image_url)

    def search_commons_image(self, search_query):
        """Ищет первую подходящую картинку через API Викисклада"""
        headers = {
            "User-Agent": "FlowerShopDemo/1.0 (https://github.com/Skip-Bug/Flower-Shop)"
        }
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {search_query}",
            "gsrnamespace": 6,
            "gsrlimit": 1,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 800,
            "format": "json",
        }

        try:
            r = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params=params,
                headers=headers,
                timeout=15,
                verify=False,
            )
            pages = r.json().get("query", {}).get("pages", {})
            if not pages:
                return None
            page = next(iter(pages.values()))
            return page.get("imageinfo", [{}])[0].get("thumburl")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  Ошибка API: {e}"))
            return None

    def download_image(self, bouquet, image_url):
        headers = {
            "User-Agent": "FlowerShopDemo/1.0 (https://github.com/Skip-Bug/Flower-Shop)",
            "Referer": "https://commons.wikimedia.org/",
        }
        try:
            response = requests.get(
                image_url, timeout=30, headers=headers, verify=False
            )
            if response.status_code != 200:
                self.stderr.write(
                    self.style.WARNING(
                        f"  Не удалось скачать (код {response.status_code})"
                    )
                )
                return

            bouquet.image.save(
                f"{bouquet.slug}.jpg",
                ContentFile(response.content),
                save=True,
            )
            self.stdout.write(self.style.SUCCESS("  Фото успешно загружено!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  Ошибка: {e}"))

    def get_bouquets_data(self):
        return [
            {
                "title": "Нежность",
                "slug": "nezhnost",
                "price": Decimal("3500.00"),
                "description": "Легкий и воздушный букет для самого близкого человека.",
                "composition": "Пионы, эустома, гортензия",
                "size": "Средний",
                "events": ["birthday", "just-because"],
                "image_query": "bouquet of white peonies",
            },
            {
                "title": "Страсть",
                "slug": "strast",
                "price": Decimal("5800.00"),
                "description": "Яркий и страстный букет для признания в любви или годовщины.",
                "composition": "Красные розы 51 шт, рускус",
                "size": "Большой",
                "events": ["birthday", "wedding"],
                "image_query": "bouquet of red roses",
            },
            {
                "title": "Весеннее настроение",
                "slug": "spring-mood",
                "price": Decimal("2500.00"),
                "description": "Свежий весенний букет из тюльпанов, который поднимет настроение.",
                "composition": "Тюльпаны 15 шт, зелень",
                "size": "Средний",
                "events": ["birthday", "just-because"],
                "image_query": "tulip bouquet",
            },
            {
                "title": "Бизнес-леди",
                "slug": "business-lady",
                "price": Decimal("7200.00"),
                "description": "Строгий, но элегантный букет для делового партнера или руководителя.",
                "composition": "Белые розы, орхидеи, сухоцветы",
                "size": "Большой",
                "events": ["corporate"],
                "image_query": "mixed flower bouquet",
            },
            {
                "title": "Бюджетный вариант",
                "slug": "budget",
                "price": Decimal("900.00"),
                "description": "Милый и аккуратный букетик, чтобы просто порадовать.",
                "composition": "Хризантемы, герберы",
                "size": "Маленький",
                "events": ["just-because", "birthday"],
                "image_query": "gerbera bouquet",
            },
            {
                "title": "Солнечный день",
                "slug": "sunny-day",
                "price": Decimal("3200.00"),
                "description": "Яркий букет из подсолнухов, который подарит улыбку.",
                "composition": "Подсолнухи 7 шт, солидаго",
                "size": "Средний",
                "events": ["birthday", "just-because"],
                "image_query": "sunflower bouquet",
            },
            {
                "title": "Розовый рассвет",
                "slug": "pink-dawn",
                "price": Decimal("4500.00"),
                "description": "Нежный и романтичный букет в пастельных тонах.",
                "composition": "Розы, эустома, бруния",
                "size": "Средний",
                "events": ["wedding"],
                "image_query": "pink rose bouquet",
            },
            {
                "title": "Мужской характер",
                "slug": "mens-character",
                "price": Decimal("6500.00"),
                "description": "Сдержанный, стильный букет с темными акцентами.",
                "composition": "Розы, сухоцветы, эвкалипт",
                "size": "Большой",
                "events": ["corporate"],
                "image_query": "chrysanthemum bouquet",
            },
            {
                "title": "Минимализм",
                "slug": "minimalism",
                "price": Decimal("800.00"),
                "description": "Один цветок, но какой! Для тех, кто ценит лаконичность.",
                "composition": "1 крупная гербера, зелень",
                "size": "Маленький",
                "events": ["just-because"],
                "image_query": "small flower bouquet",
            },
        ]
