# Инструкция по локальному запуску Uptime Checker

## Быстрый старт (без Docker)

### Предварительные требования
- Python 3.10+
- Node.js 18+
- npm 9+

### Шаг 1: Backend

```bash
# Перейдите в директорию backend
cd backend

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Запустите FastAPI сервер
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend доступен по адресу: http://localhost:8000
API документация (Swagger): http://localhost:8000/docs

### Шаг 2: Frontend (в новом терминале)

```bash
# Перейдите в директорию frontend
cd frontend

# Установите зависимости (если еще не установлены)
npm install

# Запустите dev сервер
npm run dev
```

Frontend доступен по адресу: http://localhost:3000 (или 3001 если 3000 занят)

## Проверка работы

### 1. Проверьте что Backend работает
Откройте в браузере: http://localhost:8000/health

Должно вернуться: `{"status":"healthy","database":"connected"}`

### 2. Проверьте что Frontend работает
Откройте в браузере: http://localhost:3000

Должен загрузиться дашборд

### 3. Добавьте тестовый домен

Через API (curl):
```bash
curl -X POST http://localhost:8000/api/domains \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Google\",\"url\":\"https://www.google.com\",\"check_interval_seconds\":300}"
```

Или через Swagger UI: http://localhost:8000/docs

## Примечания

### База данных
По умолчанию используется SQLite (файл `backend/uptime_db.sqlite`).
Для продакшена рекомендуется PostgreSQL.

### Celery Worker
Для полноценной работы проверок доменов требуется запустить Celery worker и Redis:

```bash
# Установка Redis (Windows)
# Скачайте с https://github.com/microsoftarchive/redis/releases
# или используйте Docker:
docker run -d -p 6379:6379 redis:7-alpine

# Запуск Celery worker (в новом терминале)
cd backend
venv\Scripts\activate
celery -A app.celery worker --loglevel=info --pool=solo

# Запуск Celery beat (планировщик)
celery -A app.celery beat --loglevel=info
```

Без Celery проверки доменов не будут выполняться автоматически.
Статус доменов останется "PENDING" до первой ручной проверки.

## Переменные окружения

Создайте файл `.env.local` в корне проекта:

```env
# SQLite (по умолчанию)
DATABASE_URL=sqlite+aiosqlite:///./backend/uptime_db.sqlite

# PostgreSQL (для продакшена)
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Redis (требуется для Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-min-32-characters

# SSL Check
SSL_WARNING_DAYS=14

# HTTP Check
HTTP_TIMEOUT=10
SLOW_THRESHOLD_MS=1500
```

## Устранение проблем

### Порт 8000 занят
```bash
# Найдите процесс
netstat -ano | findstr :8000

# Убейте процесс
taskkill /F /PID <PID>
```

### Порт 3000 занят
Vite автоматически переключится на 3001 или другой свободный порт.

### Ошибки импорта в Python
Убедитесь что активировано виртуальное окружение:
```bash
venv\Scripts\activate
```

### Frontend не видит API
Проверьте что backend запущен и доступен по http://localhost:8000

## Production запуск

### Backend
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
npm run build
# Разместите dist/ папку на nginx или другом веб-сервере
```

### База данных
Переключитесь на PostgreSQL в `.env.local`:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
```
