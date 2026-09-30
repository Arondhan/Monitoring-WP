# Uptime Checker (WowVendor Uptimer API)

Полнофункциональное веб-приложение для мониторинга доступности и производительности веб-сайтов: HTTP/HTTPS-проверки, SSL-мониторинг, WordPress-мониторинг (свежесть постов + SEO-контент), история проверок, инциденты, графики, страница настроек с прокси.

![Dashboard Preview](./docs/dashboard-preview.png)

## 🚀 Возможности

- **Мониторинг доменов** — HTTP/HTTPS эндпоинты, замер response time, ручной триггер `POST /api/domains/{id}/check`
- **Проверка SSL** — валидность сертификата, предупреждение за `SSL_WARNING_DAYS` дней, статус `SSL_ERROR`
- **WordPress-мониторинг** — детекция WP (`is_wordpress`, `wordpress_version`), последний пост (`last_post_date/title`), возраст поста `fresh (<7д) / warning (7-30д) / stale (>30д)`, сводка `GET /api/domains/wordpress/stats`, контент `GET /api/domains/{id}/content` (meta title/description + длины, h1, h2 через `app/services/wordpress.py`)
- **Real-time статус** — кэшированные поля `last_status`, `last_response_time_ms`, `uptime_percentage_24h/7d`
- **История и инциденты** — `checks` (status_code, response_time, ssl_expires_at), `incidents` (reason, severity, duration, is_resolved)
- **Безопасность доменов** — модели `domain_security_checks` (malicious links, redirects, iframes, hidden content, html/links hash) и `domain_baselines`, проверка через прокси (см. `SETTINGS_GUIDE.md`)
- **Настройки** (`/settings`) — CRUD прокси (`http/https/socks5`, `security/general`, тест через `POST /proxies/{id}/test`), `app_settings` (key-value), security/posting-настройки, дашборд `GET /api/settings/dashboard`
- **Графики** — Chart.js / vue-chartjs (uptime, response time, `UptimeChart.vue`)
- **Асинхронные проверки** — Celery worker + beat + Redis: `check_domain_task`, `check_wordpress_post_task`, `schedule_domain_checks`, `calculate_uptime_stats`, `cleanup_old_checks`; мониторинг Flower :5555
- **Темная тема** — Pinia `theme.js` (localStorage + `prefers-color-scheme`), Tailwind `dark:` классы, `ToggleSwitch.vue`

## 📋 Содержание

- [Технологический стек](#технологический-стек)
- [Быстрый старт](#быстрый-старт)
- [Локальный запуск без Docker](#локальный-запуск-без-docker)
- [Структура проекта](#структура-проекта)
- [API Документация](#api-документация)
- [Конфигурация](#конфигурация)
- [Настройки и прокси](#настройки-и-прокси)
- [Разработка](#разработка)
- [Production](#production)

Дополнительно: `RUN_LOCAL.md` — локальный запуск, `SETTINGS_GUIDE.md` — прокси и настройки, `backend/README.md` — backend-детали.

## Технологический стек

### Backend
- **FastAPI 0.109.0** — `app/main.py` (CORS `*`, lifespan init/close DB, routers: wordpress → domains → dashboard → settings → docs)
- **SQLAlchemy 2.0 (Async)** — модели `Domain`, `Check`, `Incident`, `DomainSecurityCheck`, `DomainBaseline`, `ProxyServer`, `AppSetting`; UUID (Postgres) / String(36) (SQLite) через `is_sqlite`
- **PostgreSQL 15 (Docker) / SQLite (local)** — `DATABASE_URL` (`asyncpg` / `aiosqlite`), миграции в `backend/migrations/` (`add_wordpress_fields`, `migrate_settings`), сид `backend/seed_data.py`
- **Celery 5.3.6 + Redis 7** — worker (`--concurrency=4` в compose), beat, Flower 2.0.1
- **httpx / aiohttp** — проверки, `tenacity` — ретраи, `structlog` — логи, `sslcheck` + `cryptography` — SSL
- **BeautifulSoup4 + lxml** — WP-контент и проверки безопасности

### Frontend
- **Vue 3.4 + Vite 5** — dev :3000 с proxy `/api → http://localhost:8000`, прод — сборка `dist/` + Nginx :80 (в compose проброшен как :3000)
- **Pinia** — `domains.js` (фильтры status/WordPress, сортировка), `settings.js`, `theme.js`, `api.js` (axios, `VITE_API_URL || '/api'`)
- **Vue Router** — `/` (DashboardView), `/domain/:id` (DomainDetailView), `/settings` (SettingsView)
- **Chart.js + vue-chartjs**, **TailwindCSS 3.4**, **axios**, **date-fns**
- Компоненты: `DomainCard`, `FilterBar`, `SummaryCards`, `WordPressSummaryCards`, `AddDomainModal`, `AboutModal`, `UptimeChart`, `EventLog`, `settings/ProxyManager`, `settings/WhiteListManager`, `ui/ToggleSwitch`

### Инфраструктура
- **Docker & Docker Compose** — `postgres`, `redis`, `backend`, `celery_worker`, `celery_beat`, `flower`, `frontend` (healthcheck pg/redis)
- **Nginx** — `frontend/nginx.conf`, reverse proxy для SPA

## Быстрый старт

### Требования

- Docker 20.10+, Docker Compose 2.0+, 2GB+ RAM, 1GB+ диска

### Установка

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd Dashboard
```

2. **Создайте файл окружения**
```bash
cp .env.example .env
```

3. **Отредактируйте `.env` при необходимости**
```bash
# PostgreSQL
POSTGRES_USER=uptime_user
POSTGRES_PASSWORD=uptime_pass
POSTGRES_DB=uptime_db

# Security (измените на случайную строку!)
SECRET_KEY=your-super-secret-key-min-32-characters

# SSL Check
SSL_WARNING_DAYS=14

# HTTP Check
HTTP_TIMEOUT=10
SLOW_THRESHOLD_MS=1500
```

4. **Запустите все сервисы**
```bash
docker-compose up -d
```

5. **Откройте в браузере**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (`/` — инфо `WowVendor Uptimer API`, `/health`, `/api/status`, `/project-docs`)
- API Docs (Swagger): http://localhost:8000/docs (ReDoc: `/redoc`)
- Celery Flower: http://localhost:5555

### Остановка

```bash
docker-compose down
```

Для удаления данных БД:
```bash
docker-compose down -v
```

## Локальный запуск без Docker

Кратко (подробно — `RUN_LOCAL.md`):

```bash
# Backend (http://localhost:8000, Swagger /docs, health /health)
cd backend
python -m venv venv
venv\Scripts\activate  # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (http://localhost:3000, Vite proxy /api -> :8000)
cd frontend
npm install
npm run dev
```

По умолчанию local — SQLite (`DATABASE_URL=sqlite+aiosqlite:///./uptime_db.sqlite` в `.env.local`, файл `backend/uptime_db.sqlite`). Для продакшена — PostgreSQL (`postgresql+asyncpg://...`).

Без Redis+Celery автопроверки не идут, статусы остаются `PENDING`:
```bash
docker run -d -p 6379:6379 redis:7-alpine
cd backend
celery -A app.celery worker --loglevel=info --pool=solo
celery -A app.celery beat --loglevel=info
```

Тестовый домен:
```bash
curl -X POST http://localhost:8000/api/domains \
  -H "Content-Type: application/json" \
  -d '{"name":"Google","url":"https://www.google.com","check_interval_seconds":300}'
```

## Структура проекта

```
Dashboard/
├── backend/
│   ├── app/
│   │   ├── api/           # domains.py (domains+dashboard+wordpress routers), settings.py, docs.py (/project-docs)
│   │   ├── celery/        # worker/beat задачи: check_domain_task, check_wordpress_post_task, schedule, stats, cleanup
│   │   ├── core/          # config.py (env), config_local.py
│   │   ├── db/            # session.py (Base, is_sqlite, init/close, async_session_maker)
│   │   ├── models/        # domain.py (Domain/Check/Incident), security.py, settings.py (ProxyServer/AppSetting)
│   │   ├── schemas/       # domain.py, settings.py (Pydantic, UUID->str сериализация)
│   │   ├── services/      # wordpress.py (meta/h1/h2), proxy_service.py, app_setting_service.py
│   │   └── main.py        # FastAPI app, CORS, lifespan
│   ├── migrations/        # add_wordpress_fields (.py/.sql), migrate_settings.sql
│   ├── seed_data.py       # Google/GitHub/StackOverflow
│   ├── requirements.txt
│   ├── README.md
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # DomainCard, FilterBar, SummaryCards, WordPressSummaryCards, AddDomainModal,
│   │   │                # AboutModal, UptimeChart, EventLog, settings/ProxyManager+WhiteListManager, ui/ToggleSwitch
│   │   ├── views/         # DashboardView, DomainDetailView, SettingsView
│   │   ├── stores/        # api.js, domains.js, settings.js, theme.js
│   │   ├── router/        # /, /domain/:id, /settings
│   │   ├── assets/
│   │   ├── App.vue
│   │   └── main.js
│   ├── vite.config.js     # :3000, proxy /api -> :8000
│   ├── nginx.conf
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml     # postgres, redis, backend, celery_worker, celery_beat, flower, frontend
├── .env / .env.local / .env.example
├── RUN_LOCAL.md
├── SETTINGS_GUIDE.md
└── README.md
```

## API Документация

Полная — http://localhost:8000/docs, HTML-обзор — `/project-docs`.

### Домены и мониторинг

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/domains` | Список доменов (`?status=`, пагинация) |
| POST | `/api/domains` | Добавить (`name, url, check_interval_seconds` 30–604800) |
| GET | `/api/domains/{id}` | Информация (+ `wordpress_post_age_days/status`) |
| PUT | `/api/domains/{id}` | Обновить |
| DELETE | `/api/domains/{id}` | Удалить (204) |
| POST | `/api/domains/{id}/check` | Ручная HTTP/SSL-проверка |
| GET | `/api/domains/{id}/checks` | История проверок (`?period=24h`) |
| GET | `/api/domains/{id}/incidents` | Инциденты |
| GET | `/api/domains/{id}/stats` | Статистика uptime/response |
| GET | `/api/dashboard` | Сводка дашборда |
| GET | `/api/domains/wordpress/stats` | Сводка WP (`total/fresh/warning/stale/no_posts`) |
| POST | `/api/domains/{id}/wordpress/check` | Проверить последний пост WP |
| GET | `/api/domains/{id}/content` | SEO-контент (meta title/description+h1/h2) |

### Настройки и прокси (подробно — `SETTINGS_GUIDE.md`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/settings/proxies` | Список (`?active_only, usage_type`) |
| POST | `/api/settings/proxies` | Добавить (`name, host, port, protocol http/https/socks5, usage_type security/general, ...`) |
| GET/PUT/DELETE | `/api/settings/proxies/{id}` | Получить/обновить/удалить |
| POST | `/api/settings/proxies/{id}/test` | Тест (`test_url, timeout`) |
| GET/PUT | `/api/settings/app`, `/api/settings/app/{key}` | Все настройки / одна (`?value, value_type`) |
| DELETE | `/api/settings/app/{key}` | Удалить настройку |
| GET/PUT | `/api/settings/security` | Настройки безопасности |
| GET | `/api/settings/dashboard` | Сводка (прокси counts, security/posting, AI-ключи) |

### Системные

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | `WowVendor Uptimer API`, ссылки на docs/health |
| GET | `/health` | `{"status":"healthy","database":"connected"}` |
| GET | `/api/status` | `http_timeout, slow_threshold_ms, ssl_warning_days, default_check_interval` |
| GET | `/docs`, `/redoc`, `/project-docs` | Swagger / ReDoc / HTML-обзор |

### Примеры запросов

**Добавить домен:**
```bash
curl -X POST http://localhost:8000/api/domains \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Site",
    "url": "https://example.com",
    "check_interval_seconds": 60
  }'
```

**Получить список доменов:**
```bash
curl http://localhost:8000/api/domains
```

**Получить историю проверок:**
```bash
curl http://localhost:8000/api/domains/{id}/checks?period=24h
```

## Конфигурация

### Переменные окружения

#### Backend (`app/core/config.py`, env `.env` / `.env.local`)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` (docker) или `sqlite+aiosqlite:///./uptime_db.sqlite` (local) | `sqlite+aiosqlite:///./uptime_db.sqlite` |
| `CELERY_BROKER_URL` | Redis URL для брокера | `redis://redis:6379/0` (docker) / `redis://localhost:6379/0` (local) |
| `CELERY_RESULT_BACKEND` | Redis URL для результатов | `redis://redis:6379/0` |
| `SECRET_KEY` | Секретный ключ (32+ символов!) | - |
| `SSL_WARNING_DAYS` | Дней до истечения SSL для предупреждения | `14` |
| `HTTP_TIMEOUT` | Таймаут HTTP запроса (сек) | `10` |
| `SLOW_THRESHOLD_MS` | Порог медленного ответа (мс) | `1500` |
| `OPENAI_API_KEY` / `GEMINI_API_KEY` | AI-ключи (через `.env`, нужен рестарт `uptime_backend`) | - |

#### Frontend

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `VITE_API_URL` | URL backend API | `/api` |

### Статусы доменов

| Статус | Описание | Цвет |
|--------|----------|------|
| `UP` | Сайт доступен, response time < 1500ms | 🟢 Зеленый |
| `SLOW` | Сайт доступен, response time >= 1500ms | 🟡 Желтый |
| `DOWN` | Сайт недоступен или ошибки 4xx/5xx | 🔴 Красный |
| `SSL_ERROR` | Проблема с SSL сертификатом | 🟠 Оранжевый |
| `PENDING` | Домен добавлен, проверка не выполнена | ⚪ Серый |

### Логика проверок

1. **HTTP запрос**
   - Проверка статус кода (2xx, 3xx = успех)
   - Замер времени отклика
   - Таймаут: 10 секунд

2. **SSL сертификат**
   - Проверка валидности
   - Предупреждение за 14 дней до истечения
   - Только для HTTPS

3. **Определение статуса**
   ```
   UP: 2xx/3xx && response_time < 1500ms
   SLOW: 2xx/3xx && response_time >= 1500ms
   DOWN: 4xx/5xx || timeout || connection error
   SSL_ERROR: SSL certificate expired/invalid
   ```

4. **WordPress** — возраст последнего поста: `fresh <7д`, `warning 7-30д`, `stale >30д`; контент-скан: title/description/h1/h2.

## Настройки и прокси

Кратко (полное руководство — `SETTINGS_GUIDE.md`, UI — `/settings` → `SettingsView.vue` + `ProxyManager.vue`):

- Типы прокси: `security` (проверка безопасности: вредоносные ссылки, редиректы, iframe), `general` (+ `posting`, `youtube` в планах).
- Добавление: `/settings` → «Прокси» → «+ Добавить» (name/host/port обязательно, protocol `http/https/socks5`).
- Тест: кнопка «🧪 Тест» → `✓ рабочий / ✗ не работает / ? не проверен` (`is_working`, `last_checked_at`).
- App-настройки: key-value с `value_type (string/int/float/bool/json)`, security/posting-пресеты, AI-статус — всё через `/api/settings/*` и `GET /api/settings/dashboard`.

## Разработка

### Запуск backend локально

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск PostgreSQL и Redis (через Docker)
docker-compose up -d postgres redis

# Запуск FastAPI
uvicorn app.main:app --reload --port 8000

# Запуск Celery worker (в отдельном терминале)
celery -A app.celery worker --loglevel=info

# Запуск Celery beat (в отдельном терминале)
celery -A app.celery beat --loglevel=info
```

### Запуск frontend локально

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка для production
npm run build
```

### Тестирование

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты (будущая реализация)
cd frontend
npm run test
```

Сид тестовых данных: `cd backend && python seed_data.py` (Google/GitHub/StackOverflow).

## Production

### Рекомендации

1. **Безопасность**
   - Измените `SECRET_KEY` на случайную строку 32+ символов
   - Используйте надежные пароли для PostgreSQL
   - Настройте CORS для конкретного домена (сейчас `allow_origins=["*"]` в `app/main.py`)
   - Используйте HTTPS

2. **Масштабирование**
   - Увеличьте количество Celery workers (`--concurrency=8`)
   - Настройте connection pooling для БД
   - Используйте репликацию PostgreSQL

3. **Мониторинг**
   - Включите Celery Flower для мониторинга задач
   - Настройте логирование (structlog)
   - Используйте Prometheus + Grafana

### Docker Compose для production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
    restart: always
    
  celery_worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info --concurrency=8
    restart: always
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    restart: always
```

Запуск:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Устранение проблем

### Backend не запускается

```bash
# Проверьте логи
docker-compose logs backend

# Убедитесь что БД доступна
docker-compose exec backend python -c "from app.db.session import engine; print('OK')"
```

### Celery не выполняет задачи

```bash
# Проверьте подключение к Redis
docker-compose logs celery_worker

# Перезапустите worker
docker-compose restart celery_worker
```

### Frontend не видит API

- Убедитесь что `VITE_API_URL` настроен правильно (dev proxy в `vite.config.js`: `/api → :8000`)
- Проверьте CORS настройки в backend
- Порт 3000 занят — Vite сам перейдет на 3001

### Порт 8000 занят (Windows)

```bash
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

## Лицензия

MIT License

## Contributing

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request
