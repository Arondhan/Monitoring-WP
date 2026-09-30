# Настройки и Прокси - Руководство

## 📋 Обзор

Добавлена страница настроек (`/settings`) с управлением прокси серверами для проверки безопасности доменов.

## 🌐 Прокси серверы

### Зачем нужны

Прокси используются для:
- **Проверка безопасности доменов** - обнаружение эксплойтов, вредоносных ссылок, редиректов
- **Анонимизация запросов** - скрытие реального IP при проверке доменов
- **Обход блокировок** - доступ к заблокированным ресурсам

### Типы использования

- `security` - Для проверки безопасности доменов
- `posting` - Для постинга на WordPress
- `youtube` - Для поиска YouTube видео
- `general` - Общее использование

## 🔧 API Endpoints

### Прокси серверы

```bash
# Получить список прокси
GET /api/settings/proxies?active_only=true&usage_type=security

# Добавить прокси
POST /api/settings/proxies
{
  "name": "My Proxy",
  "description": "Для проверки безопасности",
  "host": "proxy.example.com",
  "port": 8080,
  "username": "user",  # опционально
  "password": "pass",  # опционально
  "protocol": "http",  # http, https, socks5
  "usage_type": "security",
  "country": "US"
}

# Обновить прокси
PUT /api/settings/proxies/{id}

# Удалить прокси
DELETE /api/settings/proxies/{id}

# Тест прокси
POST /api/settings/proxies/{id}/test
{
  "test_url": "https://www.google.com",
  "timeout": 10
}
```

### Настройки приложения

```bash
# Получить все настройки
GET /api/settings/app

# Получить настройку по ключу
GET /api/settings/app/{key}

# Установить настройку
PUT /api/settings/app/{key}?value=123&value_type=int

# Настройки безопасности
GET /api/settings/security
PUT /api/settings/security

# Настройки постинга
GET /api/settings/posting
PUT /api/settings/posting

# Дашборд настроек
GET /api/settings/dashboard
```

## 📁 Структура БД

### Таблица `proxy_servers`

```sql
CREATE TABLE proxy_servers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(255),
    password VARCHAR(255),
    protocol VARCHAR(20) DEFAULT 'http',
    is_active BOOLEAN DEFAULT TRUE,
    is_working BOOLEAN,
    last_checked_at TIMESTAMP,
    usage_type VARCHAR(50) DEFAULT 'security',
    country VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Таблица `app_settings`

```sql
CREATE TABLE app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    value_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP
);
```

## 🎯 Использование

### 1. Добавление прокси

1. Откройте `/settings` → вкладка "Прокси"
2. Нажмите "+ Добавить прокси"
3. Заполните форму:
   - Название (обязательно)
   - Хост и порт (обязательно)
   - Логин/пароль (если требуется)
   - Протокол (http/https/socks5)
   - Тип использования (security)
4. Нажмите "Сохранить"

### 2. Тестирование прокси

1. Нажмите "🧪 Тест" на карточке прокси
2. Дождитесь результата
3. Статус обновится:
   - ✓ Рабочий (зеленый)
   - ✗ Не работает (красный)
   - ? Не проверен (серый)

### 3. Настройка безопасности

1. Откройте `/settings` → вкладка "Безопасность"
2. Включите нужные опции:
   - Использовать прокси
   - Детектирование вредоносных ссылок
   - Детектирование редиректов
   - Детектирование iframe
3. Нажмите "Сохранить настройки"

## 🔐 API ключи

AI ключи (OpenAI, Gemini) настраиваются через файл `.env`:

```bash
# Backend/.env
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-gemini-key
```

После изменения `.env` требуется перезапуск backend контейнера:

```bash
docker restart uptime_backend
```

## 📊 Мониторинг

На дашборде настроек (`/api/settings/dashboard`) отображается:
- Всего прокси
- Активных прокси
- Рабочих прокси
- Настройки безопасности
- Настройки постинга
- Статус AI ключей

## 🚀 Следующие шаги

В будущем планируется:
1. Интеграция прокси в проверку доменов
2. Детектирование вредоносных ссылок в HTML
3. Обнаружение неожиданных редиректов
4. Детектирование iframe (кликджекинг)
5. Ротация прокси для массовых проверок
