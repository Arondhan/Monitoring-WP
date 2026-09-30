"""
Страниц документации API с подробным описанием проекта
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["documentation"])


DOCS_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uptime Checker - Документация</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .nav-tabs {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .nav-tab {
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        .nav-tab:hover, .nav-tab.active {
            background: white;
            color: #667eea;
        }
        .content-section {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: none;
        }
        .content-section.active {
            display: block;
        }
        h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        h3 {
            color: #764ba2;
            margin: 30px 0 15px;
            font-size: 1.3em;
        }
        p {
            margin-bottom: 15px;
            color: #333;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 25px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        .feature-card h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        .tech-badge {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .tech-badge.backend { background: #4CAF50; }
        .tech-badge.frontend { background: #2196F3; }
        .tech-badge.infra { background: #FF9800; }
        code {
            background: #f4f4f4;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #e91e63;
        }
        pre {
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }
        pre code {
            background: none;
            color: inherit;
            padding: 0;
        }
        .status-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .status-table th, .status-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .status-table th {
            background: #667eea15;
            color: #667eea;
        }
        .status-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .status-up { background: #4CAF50; color: white; }
        .status-slow { background: #FFC107; color: black; }
        .status-down { background: #f44336; color: white; }
        .status-ssl { background: #FF9800; color: white; }
        .status-pending { background: #9e9e9e; color: white; }
        .workflow {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin: 30px 0;
        }
        .workflow-step {
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
        }
        .step-number {
            width: 40px;
            height: 40px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }
        .api-endpoint {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .api-method {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 10px;
        }
        .method-get { background: #4CAF50; color: white; }
        .method-post { background: #2196F3; color: white; }
        .method-put { background: #FF9800; color: white; }
        .method-delete { background: #f44336; color: white; }
        .note {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .note strong {
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Uptime Checker</h1>
            <p>Система мониторинга доступности веб-сайтов</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showSection('overview')">📋 Обзор</button>
            <button class="nav-tab" onclick="showSection('how-it-works')">⚙️ Как работает</button>
            <button class="nav-tab" onclick="showSection('tech-stack')">🛠 Технологии</button>
            <button class="nav-tab" onclick="showSection('api')">📡 API</button>
            <button class="nav-tab" onclick="showSection('statuses')">📊 Статусы</button>
        </div>

        <!-- Обзор -->
        <div id="overview" class="content-section active">
            <h2>📖 Что такое Uptime Checker?</h2>
            <p>
                <strong>Uptime Checker</strong> — это современная система для автоматического мониторинга 
                доступности и производительности веб-сайтов. Она периодически проверяет указанные вами сайты 
                и сообщает, если они становятся недоступны или работают медленно.
            </p>
            
            <div class="note">
                <strong>💡 Для обычного пользователя:</strong> Вы добавляете адреса сайтов, которые хотите 
                отслеживать, и система автоматически проверяет их каждые N минут/часов. Если сайт "упал" 
                или работает медленно — вы сразу об этом узнаете.
            </div>

            <h3>🎯 Основные возможности</h3>
            <div class="feature-grid">
                <div class="feature-card">
                    <h4>🌐 Мониторинг доменов</h4>
                    <p>Добавляйте любые веб-сайты для отслеживания их доступности 24/7</p>
                </div>
                <div class="feature-card">
                    <h4>🔒 SSL мониторинг</h4>
                    <p>Автоматическая проверка срока действия SSL сертификатов с предупреждениями</p>
                </div>
                <div class="feature-card">
                    <h4>⚡ Real-time статус</h4>
                    <p>Мгновенное отображение текущего состояния всех отслеживаемых сайтов</p>
                </div>
                <div class="feature-card">
                    <h4>📈 История проверок</h4>
                    <p>Детальная история всех проверок с временем отклика для каждого сайта</p>
                </div>
                <div class="feature-card">
                    <h4>🚨 Инциденты</h4>
                    <p>Автоматическое отслеживание простоев и проблем с сайтами</p>
                </div>
                <div class="feature-card">
                    <h4>📊 Графики и статистика</h4>
                    <p>Визуализация uptime и времени отклика за разные периоды</p>
                </div>
            </div>

            <h3>🎛 Панель управления</h3>
            <p>
                Веб-интерфейс предоставляет удобную панель управления, где вы можете:
            </p>
            <ul>
                <li>➕ <strong>Добавлять новые домены</strong> для мониторинга</li>
                <li>👁 <strong>Просматривать статус</strong> всех сайтов в реальном времени</li>
                <li>📉 <strong>Анализировать графики</strong> времени ответа и uptime</li>
                <li>🔍 <strong>Фильтровать и сортировать</strong> домены по различным параметрам</li>
                <li>⚙️ <strong>Настраивать интервал</strong> проверки для каждого домена</li>
            </ul>
        </div>

        <!-- Как работает -->
        <div id="how-it-works" class="content-section">
            <h2>⚙️ Как работает система</h2>
            
            <div class="workflow">
                <div class="workflow-step">
                    <div class="step-number">1</div>
                    <div>
                        <h4>Добавление домена</h4>
                        <p>Вы добавляете URL сайта через веб-интерфейс или API, указывая желаемый интервал проверки (от 30 секунд до 7 дней).</p>
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="step-number">2</div>
                    <div>
                        <h4>Планировщик задач (Celery Beat)</h4>
                        <p>Фоновый сервис каждые 10 секунд проверяет, какие домены нужно проверить, и создает задачи для Celery Worker.</p>
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="step-number">3</div>
                    <div>
                        <h4>Выполнение проверки (Celery Worker)</h4>
                        <p>
                            Worker выполняет HTTP/HTTPS запрос к сайту и измеряет:
                        </p>
                        <ul>
                            <li>• <strong>HTTP статус код</strong> (200, 301, 404, 500 и т.д.)</li>
                            <li>• <strong>Время отклика</strong> в миллисекундах</li>
                            <li>• <strong>SSL сертификат</strong> (срок действия, валидность)</li>
                        </ul>
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="step-number">4</div>
                    <div>
                        <h4>Определение статуса</h4>
                        <p>
                            На основе результатов проверки система определяет статус:
                        </p>
                        <ul>
                            <li>• <strong>UP</strong> — сайт доступен, время ответа < 1500мс</li>
                            <li>• <strong>SLOW</strong> — сайт доступен, но время ответа ≥ 1500мс</li>
                            <li>• <strong>DOWN</strong> — сайт недоступен или ошибка 4xx/5xx</li>
                            <li>• <strong>SSL_ERROR</strong> — проблема с SSL сертификатом</li>
                        </ul>
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="step-number">5</div>
                    <div>
                        <h4>Сохранение результатов</h4>
                        <p>
                            Результаты проверки сохраняются в базу данных PostgreSQL, обновляется статистика домена.
                        </p>
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="step-number">6</div>
                    <div>
                        <h4>Обработка инцидентов</h4>
                        <p>
                            При обнаружении проблемы (DOWN/SSL_ERROR) автоматически создается инцидент. 
                            Когда сайт восстанавливается — инцидент закрывается с указанием длительности простоя.
                        </p>
                    </div>
                </div>
            </div>

            <h3>🔄 Архитектура системы</h3>
            <pre><code>┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│    Backend   │────▶│  PostgreSQL │
│  (Vue 3)    │◀────│   (FastAPI)  │◀────│  (Database) │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │    Redis     │
                    │   (Broker)   │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
       ┌──────▼──────┐          ┌──────▼──────┐
       │   Celery    │          │   Celery    │
       │   Worker    │          │    Beat     │
       │  (Checks)   │          │(Scheduler)  │
       └─────────────┘          └─────────────┘</code></pre>
        </div>

        <!-- Технологии -->
        <div id="tech-stack" class="content-section">
            <h2>🛠 Технологический стек</h2>
            
            <h3>Backend (Серверная часть)</h3>
            <div class="tech-stack">
                <span class="tech-badge backend">Python 3.11</span>
                <span class="tech-badge backend">FastAPI</span>
                <span class="tech-badge backend">SQLAlchemy</span>
                <span class="tech-badge backend">AsyncPG</span>
                <span class="tech-badge backend">Celery</span>
                <span class="tech-badge backend">Redis</span>
                <span class="tech-badge backend">httpx</span>
                <span class="tech-badge backend">Pydantic</span>
            </div>
            
            <h4>📦 Ключевые библиотеки:</h4>
            <ul>
                <li>
                    <code>FastAPI</code> — современный веб-фреймворк для создания API. 
                    Обеспечивает высокую производительность и автоматическую документацию.
                </li>
                <li>
                    <code>SQLAlchemy + AsyncPG</code> — ORM и асинхронный драйвер для работы 
                    с базой данных PostgreSQL. Позволяют выполнять запросы без блокировки.
                </li>
                <li>
                    <code>Celery</code> — распределенная очередь задач. Используется для 
                    фоновых проверок сайтов без блокировки основного приложения.
                </li>
                <li>
                    <code>Redis</code> — in-memory база данных, используется как брокер 
                    сообщений для Celery.
                </li>
                <li>
                    <code>httpx</code> — асинхронный HTTP-клиент для выполнения запросов 
                    к отслеживаемым сайтам.
                </li>
                <li>
                    <code>Pydantic</code> — валидация данных и сериализация. 
                    Гарантирует корректность входящих и исходящих данных.
                </li>
            </ul>

            <h3>Frontend (Клиентская часть)</h3>
            <div class="tech-stack">
                <span class="tech-badge frontend">Vue 3</span>
                <span class="tech-badge frontend">Vite</span>
                <span class="tech-badge frontend">Pinia</span>
                <span class="tech-badge frontend">Vue Router</span>
                <span class="tech-badge frontend">Chart.js</span>
                <span class="tech-badge frontend">TailwindCSS</span>
                <span class="tech-badge frontend">Axios</span>
                <span class="tech-badge frontend">date-fns</span>
            </div>
            
            <h4>📦 Ключевые библиотеки:</h4>
            <ul>
                <li>
                    <code>Vue 3</code> — прогрессивный JavaScript-фреймворк для создания 
                    пользовательских интерфейсов.
                </li>
                <li>
                    <code>Vite</code> — быстрый сборщик проектов. Обеспечивает мгновенную 
                    перезагрузку при разработке.
                </li>
                <li>
                    <code>Pinia</code> — менеджер состояния приложения. Хранит данные о 
                    доменах и настройках.
                </li>
                <li>
                    <code>Chart.js</code> — библиотека для построения графиков. 
                    Визуализирует uptime и время ответа.
                </li>
                <li>
                    <code>TailwindCSS</code> — утилитарный CSS-фреймворк. 
                    Обеспечивает современный дизайн.
                </li>
                <li>
                    <code>date-fns</code> — работа с датами. 
                    Форматирует время проверок.
                </li>
            </ul>

            <h3>Инфраструктура</h3>
            <div class="tech-stack">
                <span class="tech-badge infra">Docker</span>
                <span class="tech-badge infra">Docker Compose</span>
                <span class="tech-badge infra">PostgreSQL 15</span>
                <span class="tech-badge infra">Redis 7</span>
                <span class="tech-badge infra">Nginx</span>
            </div>
        </div>

        <!-- API -->
        <div id="api" class="content-section">
            <h2>📡 API Документация</h2>
            <p>
                Система предоставляет REST API для программного управления. 
                Все эндпоинты возвращают данные в формате JSON.
            </p>

            <h3>📍 Основные эндпоинты</h3>
            
            <div class="api-endpoint">
                <span class="api-method method-get">GET</span>
                <code>/api/domains</code>
                <p>Получить список всех доменов с фильтрацией и сортировкой</p>
                <p><strong>Параметры:</strong> <code>status</code>, <code>sort_by</code>, <code>sort_order</code>, <code>limit</code>, <code>offset</code></p>
            </div>

            <div class="api-endpoint">
                <span class="api-method method-post">POST</span>
                <code>/api/domains</code>
                <p>Добавить новый домен для мониторинга</p>
                <p><strong>Тело запроса:</strong></p>
                <pre><code>{
  "url": "https://example.com",
  "name": "Example Site",
  "check_interval_seconds": 300
}</code></pre>
            </div>

            <div class="api-endpoint">
                <span class="api-method method-get">GET</span>
                <code>/api/domains/{id}</code>
                <p>Получить информацию о конкретном домене</p>
            </div>

            <div class="api-endpoint">
                <span class="api-method method-put">PUT</span>
                <code>/api/domains/{id}</code>
                <p>Обновить информацию о домене</p>
            </div>

            <div class="api-endpoint">
                <span class="api-method method-delete">DELETE</span>
                <code>/api/domains/{id}</code>
                <p>Удалить домен из мониторинга</p>
            </div>

            <div class="api-endpoint">
                <span class="api-method method-get">GET</span>
                <code>/api/domains/{id}/checks</code>
                <p>Получить историю проверок домена</p>
                <p><strong>Параметры:</strong> <code>period</code> (1h, 6h, 24h, 7d, 30d)</p>
            </div>

            <div class="api-endpoint">
                <span class="api-method method-get">GET</span>
                <code>/api/domains/{id}/incidents</code>
                <p>Получить список инцидентов для домена</p>
            </div>

            <div class="api-endpoint">
                <span class="api-method method-get">GET</span>
                <code>/api/dashboard</code>
                <p>Получить сводку дашборда (общая статистика)</p>
            </div>

            <div class="note">
                <strong>📚 Полная документация API</strong> доступна по адресу 
                <a href="/docs" target="_blank">/docs</a> (Swagger UI) или 
                <a href="/redoc" target="_blank">/redoc</a> (ReDoc).
            </div>
        </div>

        <!-- Статусы -->
        <div id="statuses" class="content-section">
            <h2>📊 Статусы доменов</h2>
            <p>
                Система определяет 5 различных статусов для каждого домена:
            </p>

            <table class="status-table">
                <thead>
                    <tr>
                        <th>Статус</th>
                        <th>Описание</th>
                        <th>Условие</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><span class="status-badge status-up">UP</span></td>
                        <td>Сайт доступен и работает нормально</td>
                        <td>HTTP 2xx/3xx && response_time < 1500мс</td>
                    </tr>
                    <tr>
                        <td><span class="status-badge status-slow">SLOW</span></td>
                        <td>Сайт доступен, но отвечает медленно</td>
                        <td>HTTP 2xx/3xx && response_time ≥ 1500мс</td>
                    </tr>
                    <tr>
                        <td><span class="status-badge status-down">DOWN</span></td>
                        <td>Сайт недоступен или возвращает ошибку</td>
                        <td>HTTP 4xx/5xx || timeout || connection error</td>
                    </tr>
                    <tr>
                        <td><span class="status-badge status-ssl">SSL_ERROR</span></td>
                        <td>Проблема с SSL сертификатом</td>
                        <td>SSL certificate expired/invalid</td>
                    </tr>
                    <tr>
                        <td><span class="status-badge status-pending">PENDING</span></td>
                        <td>Домен добавлен, проверка еще не выполнена</td>
                        <td>Первая проверка не завершена</td>
                    </tr>
                </tbody>
            </table>

            <h3>🔍 Логика проверок</h3>
            
            <h4>1. HTTP запрос</h4>
            <ul>
                <li>Проверка статус кода (2xx, 3xx = успех)</li>
                <li>Замер времени отклика в миллисекундах</li>
                <li>Таймаут запроса: 10 секунд</li>
                <li>Follow redirects: включен</li>
            </ul>

            <h4>2. SSL сертификат (только для HTTPS)</h4>
            <ul>
                <li>Проверка валидности сертификата</li>
                <li>Предупреждение за 14 дней до истечения</li>
                <li>Извлечение даты истечения</li>
            </ul>

            <h4>3. Определение статуса</h4>
            <pre><code>UP:         2xx/3xx && response_time < 1500ms
SLOW:       2xx/3xx && response_time >= 1500ms
DOWN:       4xx/5xx || timeout || connection error
SSL_ERROR:  SSL certificate expired/invalid</code></pre>

            <h3>⏱ Интервалы проверки</h3>
            <p>
                Вы можете настроить интервал проверки для каждого домена индивидуально:
            </p>
            <ul>
                <li>• <strong>Минимум:</strong> 30 секунд</li>
                <li>• <strong>Максимум:</strong> 7 дней (604 800 секунд)</li>
                <li>• <strong>По умолчанию:</strong> 60 секунд</li>
            </ul>
            <p>
                <strong>Быстрые пресеты:</strong> 1 мин, 5 мин, 15 мин, 30 мин, 1 час, 12 часов, 1 день, 2 дня, 1 неделя
            </p>
        </div>
    </div>

    <script>
        function showSection(sectionId) {
            // Скрыть все секции
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Показать выбранную секцию
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""


@router.get("/project-docs", response_class=HTMLResponse)
async def project_docs():
    """Страниц документации проекта с подробным описанием"""
    return DOCS_HTML
