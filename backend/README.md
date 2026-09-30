# Uptime Checker - Backend

Backend для системы мониторинга доступности веб-сайтов.

## Технологии

- **FastAPI** - Веб-фреймворк
- **SQLAlchemy (Async)** - ORM для работы с БД
- **PostgreSQL** - База данных
- **Celery** - Очереди задач для фоновых проверок
- **Redis** - Брокер сообщений для Celery
- **httpx** - Асинхронный HTTP клиент
- **structlog** - Структурированное логгирование

## Структура проекта

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── celery/        # Celery задачи
│   ├── core/          # Конфигурация и утилиты
│   ├── db/            # Подключение к БД
│   ├── models/        # SQLAlchemy модели
│   ├── schemas/       # Pydantic схемы
│   └── main.py        # Точка входа
├── requirements.txt
└── Dockerfile
```

## Запуск

### Через Docker Compose (рекомендуется)

```bash
# Из корня проекта
docker-compose up -d backend celery_worker celery_beat
```

### Локальная разработка

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Копирование .env
cp .env.example .env

# Запуск миграций (создание таблиц)
# Таблицы создаются автоматически при старте

# Запуск FastAPI
uvicorn app.main:app --reload

# Запуск Celery worker (в отдельном терминале)
celery -A app.celery worker --loglevel=info

# Запуск Celery beat (в отдельном терминале)
celery -A app.celery beat --loglevel=info
```

## API Endpoints

### Domains

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/domains` | Список доменов |
| POST | `/api/domains` | Добавить домен |
| GET | `/api/domains/{id}` | Информация о домене |
| PUT | `/api/domains/{id}` | Обновить домен |
| DELETE | `/api/domains/{id}` | Удалить домен |
| GET | `/api/domains/{id}/checks` | История проверок |
| GET | `/api/domains/{id}/incidents` | Инциденты |
| GET | `/api/domains/{id}/stats` | Статистика |

### Dashboard

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/dashboard` | Сводка дашборда |

### System

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Информация об API |
| GET | `/health` | Проверка здоровья |
| GET | `/docs` | Swagger документация |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | - |
| `CELERY_BROKER_URL` | URL Redis брокера | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | URL Redis для результатов | `redis://localhost:6379/0` |
| `SECRET_KEY` | Секретный ключ | - |
| `SSL_WARNING_DAYS` | Дней до истечения SSL для предупреждения | `14` |
| `HTTP_TIMEOUT` | Таймаут HTTP запроса (сек) | `10` |
| `SLOW_THRESHOLD_MS` | Порог медленного ответа (мс) | `1500` |

## Логика проверок

### Статусы доменов

- **UP** - Код 2xx/3xx, время отклика < 1500ms
- **SLOW** - Код 2xx/3xx, время отклика >= 1500ms
- **DOWN** - Код 4xx/5xx, таймаут, ошибка соединения
- **SSL_ERROR** - Проблема с SSL сертификатом
- **SSL_WARNING** - SSL истекает в ближайшие N дней

### Проверки

1. **HTTP запрос** - Проверка доступности и времени отклика
2. **SSL сертификат** - Проверка срока действия
3. **Таймаут** - Максимум 10 секунд на ответ

## Celery задачи

- `check_domain_task` - Проверка одного домена
- `schedule_domain_checks` - Планировщик проверок (каждые 10 сек)
- `calculate_uptime_stats` - Пересчет статистики (каждые 5 мин)
- `cleanup_old_checks` - Очистка старых записей

## Мониторинг Celery

Flower доступен по адресу `http://localhost:5555`

```bash
docker-compose up flower
```
