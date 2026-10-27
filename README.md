# FlowerShop

Сайт цветочного магазина в Красноярске. Букеты со смыслом.

## Стек

- Python 3.13
- Django 5.2 LTS
- SQLite (на старте)

## Локальный запуск

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # заполнить SECRET_KEY
python manage.py migrate
python manage.py runserver
```
