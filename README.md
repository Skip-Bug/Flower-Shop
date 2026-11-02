# FlowerShop

[![GitHub Репозиторий](https://img.shields.io/badge/Репозиторий-GitHub-blue?logo=github)](https://github.com/Skip-Bug/Flower-Shop)
[![Лицензия MIT](https://img.shields.io/badge/Лицензия-MIT-blue.svg)](LICENSE)
[![Демо сайта](https://img.shields.io/badge/Демо-сайт-brightgreen)](https://skip-project.localhost.cc)

<img width="907" height="630" alt="Screenshot 2026-11-02 132136" src="https://github.com/user-attachments/assets/0c39cbd8-d767-48c7-9a7a-6fb81a375ffb" />

Сайт красноярского цветочного магазина. Букеты со смыслом.

Клиент выбирает букет из каталога или проходит квиз для подбора, оформляет заказ с адресом и временем доставки, применяет промокод и оплачивает онлайн через ЮKassa или наличными при получении.

## Возможности

- Каталог букетов с фильтрацией по событиям (день рождения, свадьба, корпоратив)
- Квиз-подбор букета по поводу и бюджету
- Оформление заказа: адрес, время доставки, способ оплаты
- Промокоды: скидка процентом или фиксированной суммой
- Оплата картой онлайн (ЮKassa) или наличными при получении
- Заявка на консультацию — флорист свяжется с клиентом
- Админ-панель: заказы, букеты, промокоды, настройки доставки
- Дашборд флориста — список активных заказов со статусами

<img width="1049" height="369" alt="image" src="https://github.com/user-attachments/assets/040d8083-21be-4b5c-b8b5-8127321ae0cc" />

## Требования

- Python 3.13+

```bash
python --version
```

## Как запустить проект локально

- Клонируйте репозиторий и перейдите в папку проекта:

  ```bash
  git clone https://github.com/Skip-Bug/Flower-Shop.git
  cd Flower-Shop
  ```

- Создайте и активируйте виртуальное окружение:

  ```bash
  python -m venv .venv
  # Windows
  .venv\Scripts\activate
  # Linux/Mac
  source .venv/bin/activate
  ```

- Установите зависимости:

  ```bash
  pip install -r requirements.txt
  ```

- Создайте файл `.env` в корне проекта и заполните его:

  ```
  # Обязательно
  SECRET_KEY=ваш-секретный-ключ

  # Обязательно для разработки
  DEBUG=True
  ALLOWED_HOSTS=127.0.0.1,localhost

  # Обязательно для продакшена
  # DATABASE_URL=postgres://flower_user:пароль!@host:5432/flower_shop
  # YOOKASSA_SHOP_ID=номер_от_юкассы
  # YOOKASSA_SECRET_KEY=ваш_ключ_юкассы
  # CSRF_TRUSTED_ORIGINS=["https://ваш-домен.com"]
  ```

  Файл `.env` **не коммитится** в Git — он уже добавлен в `.gitignore`.

- Примените миграции:

  ```bash
  python manage.py migrate
  ```

- Заполните базу демо-данными (букеты, события, фото):

  ```bash
  python manage.py seed_demo
  ```

- Создайте суперпользователя для доступа в админку:

  ```bash
  python manage.py createsuperuser
  ```

- Запустите сервер разработки:

  ```bash
  python manage.py runserver
  ```

Сайт будет доступен по адресу http://127.0.0.1:8000/, админка — http://127.0.0.1:8000/admin/, страница флориста — http://127.0.0.1:8000/florist только для администраторов.

## База данных

По умолчанию используется SQLite — файл `db.sqlite3` создаётся автоматически при первом запуске `python manage.py migrate`. В продакшене подключается PostgreSQL через переменную `DATABASE_URL`.

Файл базы данных не коммитится в Git (добавлен в `.gitignore`).

## Линтинг

Код проверяется и форматируется линтером [ruff](https://docs.astral.sh/ruff/) (настройки в `pyproject.toml`).

```bash
ruff check .
ruff format .
```

Через pre-commit (проверка перед каждым коммитом):

```bash
pre-commit install
pre-commit run --all-files
```

## Зависимости проекта

Все зависимости зафиксированы в `requirements.txt`:

Для разработки дополнительно устанавливаются из `requirements-dev.txt`.
