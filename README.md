# News Blog

Новостной блог на Django с системой ролей, публикацией и модерацией статей, комментариями, лайками, закладками, REST API, PostgreSQL, Redis и Docker.

Проект реализует полный цикл работы со статьёй: пользователь может стать автором, создать черновик, отправить его на модерацию, а сотрудник сайта — опубликовать или отклонить материал.

## Демо

https://news-blog-b0ju.onrender.com/

## Основные возможности

- регистрация и вход по имени пользователя или email;
- профиль пользователя и профиль автора;
- роли пользователя, автора и сотрудника;
- создание, редактирование и удаление собственных статей;
- статусы статей: черновик, отправлена на модерацию, опубликована, отклонена;
- очередь модерации для сотрудников;
- категории и теги;
- поиск и фильтрация статей;
- лайки и закладки;
- создание, редактирование и удаление комментариев;
- REST API;
- JWT-аутентификация для API;
- Swagger-документация;
- Redis-кэширование;
- собственные страницы ошибок 400, 403, 404 и 500;
- автоматические тесты и GitHub Actions.

## Роли

### Гость

Может просматривать опубликованные статьи, пользоваться поиском и фильтрами.

### Зарегистрированный пользователь

Дополнительно может:

- редактировать профиль;
- ставить лайки;
- добавлять статьи в закладки;
- оставлять и редактировать свои комментарии;
- просматривать профили авторов.

### Автор

Дополнительно может:

- создавать статьи;
- редактировать черновики и отклонённые статьи;
- отправлять статьи на модерацию;
- удалять собственные статьи;
- отслеживать статус публикации.

### Сотрудник

Может просматривать очередь модерации, публиковать или отклонять статьи и оставлять комментарий к решению.

## Жизненный цикл статьи

```text
Черновик
   ↓
Отправлена на модерацию
   ↓
Модерация
   ├── Опубликована
   └── Отклонена
          ↓
     Редактирование
          ↓
     Повторная отправка
```

## Технологии

**Backend**

- Python 3.14
- Django 6.1.2
- Django REST Framework
- SimpleJWT
- django-filter
- drf-spectacular

**База данных и инфраструктура**

- PostgreSQL 17
- Redis
- Docker
- Docker Compose
- WhiteNoise
- Yandex Object Storage

**Frontend**

- Django Templates
- HTML
- CSS
- JavaScript

**Разработка и тестирование**

- Django Debug Toolbar
- Django TestCase
- DRF APITestCase
- GitHub Actions

## Структура проекта

```text
blog-prog/
├── accounts/          # пользователи, авторизация и профили
├── articles/          # статьи, категории, теги и модерация
├── interactions/      # комментарии, лайки и закладки
├── core/              # настройки проекта, маршрутизация и middleware
├── static/            # CSS и JavaScript
├── templates/         # общие шаблоны и страницы ошибок
├── .github/workflows/ # GitHub Actions
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

## REST API

Основные endpoints:

```text
/api/articles/
/api/categories/
/api/tags/
/api/comments/
```

JWT:

```text
/api/token/
/api/token/refresh/
```

Документация API:

```text
/api/docs/
/api/schema/
```

## Запуск проекта

Клонировать репозиторий:

```bash
git clone https://github.com/sali-sultanova1/blog-prog.git
cd blog-prog
```

Создать локальный `.env` на основе примера:

```bash
cp .env.example .env
```

При необходимости изменить значения в `.env`, затем собрать и запустить контейнеры:

```bash
docker compose up -d --build
```

Применить миграции:

```bash
docker compose exec web python manage.py migrate
```

Создать администратора:

```bash
docker compose exec web python manage.py createsuperuser
```

После запуска:

```text
Сайт:       http://localhost:8000/
Admin:      http://localhost:8000/admin/
Swagger:    http://localhost:8000/api/docs/
```

Файл с примером необходимых переменных окружения находится в `.env.example`. Настоящий `.env` не хранится в репозитории.

## Тестирование

В проекте предусмотрено 43 автоматических теста: тесты авторизации, web-логики, REST API, сериализаторов и полного сценария публикации статьи.

Запуск:

```bash
docker compose exec web python manage.py test
```

Дополнительные проверки:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
```

## GitHub Actions

Workflow находится в:

```text
.github/workflows/tests.yml
```

При `push` и `pull_request` GitHub Actions собирает Docker-образ, запускает PostgreSQL и Redis и выполняет тесты проекта.

## Автор

Итоговый учебный проект по Python и Django.

## Тестовые данные для входа

```
s_test
passtest123
```

