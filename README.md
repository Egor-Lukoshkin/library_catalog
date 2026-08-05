# Library Catalog API

Асинхронный REST API для управления библиотечным каталогом. Приложение позволяет создавать, получать, изменять, удалять и фильтровать книги. При создании книги API пытается автоматически дополнить данные сведениями из Open Library. Если внешний сервис недоступен, книга всё равно сохраняется.

## Технологии

- Python 3.11+
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0 и asyncpg
- Alembic
- Pydantic 2
- HTTPX
- Poetry
- Docker Compose
- Pytest
- Ruff, Black и mypy

## Возможности

- CRUD-операции с книгами;
- получение книги по UUID;
- фильтрация по названию, автору, жанру, году и доступности;
- частичный регистронезависимый поиск по названию и автору;
- точное совпадение жанра;
- пагинация через `limit` и `offset`;
- проверка уникальности ISBN;
- обогащение данных через Open Library;
- graceful degradation при недоступности Open Library;
- Swagger UI и ReDoc.

## Структура проекта

```text
library_catalog/
├── alembic/                    # Миграции базы данных
├── src/
│   └── library_catalog/
│       ├── api/                # Роутеры, схемы и зависимости FastAPI
│       ├── core/               # Конфигурация, БД, логирование, исключения
│       ├── data/               # ORM-модели и репозитории
│       ├── domain/             # Сервисы, доменные ошибки и мапперы
│       ├── external/           # HTTP-клиент и интеграция Open Library
│       └── main.py             # Точка входа приложения
├── tests/                      # Автоматические тесты
├── .env.example               # Пример переменных окружения
├── alembic.ini                # Конфигурация Alembic
├── docker-compose.yml         # PostgreSQL в Docker
├── pyproject.toml             # Зависимости и настройки проекта
└── README.md
```

## Требования

Перед запуском должны быть установлены:

- Python 3.11 или новее;
- Poetry;
- Docker и Docker Compose.

## Установка

Из корневой директории проекта установите зависимости:

```bash
poetry install
```

Создайте локальный файл конфигурации:

```bash
cp .env.example .env
```

В PowerShell:

```powershell
Copy-Item .env.example .env
```

## Переменные окружения

Пример находится в `.env.example`:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/library_catalog
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO
```

Основная обязательная переменная — `DATABASE_URL`. Она должна содержать URL PostgreSQL с async-драйвером `asyncpg`.

## Запуск PostgreSQL

Запустите контейнер базы данных:

```bash
docker compose up -d postgres
```

Проверьте состояние контейнера:

```bash
docker compose ps
```

## Миграции

Примените все миграции:

```bash
poetry run alembic upgrade head
```

Проверьте текущую версию:

```bash
poetry run alembic current
```

## Запуск приложения

```bash
poetry run uvicorn src.library_catalog.main:app --reload
```

После запуска доступны:

- API: `http://127.0.0.1:8000`;
- Swagger UI: `http://127.0.0.1:8000/docs`;
- ReDoc: `http://127.0.0.1:8000/redoc`;
- health check: `http://127.0.0.1:8000/health`.

## Основные эндпоинты

| Метод | URL | Назначение |
|---|---|---|
| `POST` | `/api/v1/books` | Создать книгу |
| `GET` | `/api/v1/books` | Получить список и применить фильтры |
| `GET` | `/api/v1/books/{book_id}` | Получить книгу по UUID |
| `PATCH` | `/api/v1/books/{book_id}` | Частично обновить книгу |
| `DELETE` | `/api/v1/books/{book_id}` | Удалить книгу |

Параметры списка: `title`, `author`, `genre`, `year`, `available`, `limit`, `offset`.

## Запуск тестов

Тесты используют отдельную базу `library_catalog_test`. Создайте её один раз после запуска PostgreSQL:

```bash
docker compose exec postgres psql -U postgres -d postgres -c "CREATE DATABASE library_catalog_test;"
```

Затем запустите тесты:

```bash
poetry run pytest
```

Отдельный тестовый модуль:

```bash
poetry run pytest tests/test_books.py -v
```

## Проверка качества кода

```bash
poetry run ruff check .
poetry run black --check .
poetry run mypy src
```

Для автоматического форматирования:

```bash
poetry run black .
```

## Open Library

При создании книги сервис сначала пытается найти данные по ISBN, затем — по названию и автору. Полученные сведения сохраняются в поле `extra`. Ошибка сети, таймаут или некорректный ответ Open Library не отменяют создание книги: сервис записывает предупреждение в лог и сохраняет книгу без внешнего обогащения.
