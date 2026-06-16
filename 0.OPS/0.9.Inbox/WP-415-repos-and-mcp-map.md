# Карта репозиториев: MCP и локальный доступ

---

## Архитектурный принцип

Репо делятся на два типа доступа:

| Тип | Кому нужен | Как работает |
|-----|-----------|-------------|
| **Через Aisystant MCP** | Всем (и людям, и облачным агентам) | Содержимое индексировано, поиск через инструменты MCP — клонировать не нужно |
| **Локальный клон** | Разработчикам с VS Code | Нужен для написания кода, коммитов, отладки |

Правило: если ты **читаешь знание** из репо — используй MCP. Если **пишешь код** в репо — клонируй локально.

---

## Секция 1: Репо, доступные через Aisystant MCP

Эти репо индексируются в `knowledge-mcp` и `guides-mcp`. Доступ — через инструменты MCP, не через клон.

**Подключение:** `mcp.aisystant.com` (OAuth через Ory). Один URL для всех.

### Основания (ZP / FPF / SPF)

| Репо | GitHub | Что содержит |
|------|--------|-------------|
| Нулевые принципы | `TserenTserenov/ZP` | Онтологический базис |
| Первые принципы | `ailev/FPF` | Методологический фундамент (Андрей Левенчук) |
| Вторые принципы | `TserenTserenov/SPF` | Системное мышление — учебная база |

### Pack-репо (доменное знание)

| Репо | GitHub | Что содержит |
|------|--------|-------------|
| Платформенные контракты | `TserenTserenov/PACK-digital-platform` | Обещания (DP.SC.*), роли (DP.ROLE.*), архитектура |
| Методология и программы | `TserenTserenov/PACK-MIM` | Ступени, методы развития, курсы |
| Правила агентов | `TserenTserenov/PACK-agent-rules` | AR.* правила, которые исполняют агенты |
| Верификация | `TserenTserenov/PACK-verification` | Роли и методы проверки |
| Экосистема | `TserenTserenov/PACK-ecosystem` | Устройство экосистемы Aisystant |
| Личностное развитие | `aisystant/PACK-personal` | cp-профиль, ступени мастерства |
| Риторика | `TserenTserenov/PACK-rhetoric` | Коммуникация и убеждение |
| Автономные агенты | `TserenTserenov/PACK-autonomous-agents` | Агентные паттерны |

### Governance и программы

| Репо | GitHub | Что содержит |
|------|--------|-------------|
| Описание экосистемы | `aisystant/DS-ecosystem-development` | Карта всей системы (A/B/C-ядра), службы, роли команды |
| Учебная программа | `aisystant/DS-principles-curriculum` | Курс по принципам мышления |
| Документация платформы | `aisystant/docs` | Пользовательская документация |

---

## Секция 2: Репо для локального клона в VS Code

Эти репо нужны для разработки. Клонировать в `~/IWE/DS-IT-systems/` или `~/IWE/DS-MCP/`.

### MCP-сервисы

| Репо | GitHub | Назначение |
|------|--------|-----------|
| MCP-шлюз | `aisystant/gateway-mcp` | Единая точка входа, OAuth, маршрутизация |
| Поиск знаний | `aisystant/knowledge-mcp` | Векторный поиск по Pack и базам знаний |
| Память.Derived | `aisystant/digital-twin-mcp` | Показатели прогресса, цифровой двойник |
| Личные знания | `aisystant/personal-knowledge-mcp` | Личные репо пользователя |
| Каталог программ | `aisystant/guides-mcp` | Руководства и программы развития |
| Конечный автомат | `aisystant/fsm-mcp` | FSM-ассистент |
| Запись событий | `aisystant/event-gateway` | Единственный writer в journal (CF Worker) |
| Запуск агентов | `aisystant/agent-runner` | Серверный запуск headless-агентов |
| Статус агентов | `aisystant/agent-status-service` | Реестр активных агентов |
| Контроль scope | `aisystant/bridge-scope-service` | Проверка прав на write-операции |
| Интеграция с GitHub | `aisystant/github-integration-service` | Управление GitHub-организациями и доступами (WP-415) |
| Локальный шлюз | `TserenTserenov/iwe-local-gateway` | MCP для VS Code (multi-agent coordination) |

### Сервисы приложения

| Репо | GitHub | Назначение |
|------|--------|-----------|
| Telegram-бот | `aisystant/aist_bot` | Основной бот (@aist_me_bot, @aist_pilot_me) |
| Сборщик событий | `aisystant/activity-hub` | Medallion: bronze/silver/gold |
| Проекции событий | `aisystant/multi-domain-projection-worker` | domain_event → persona/subscription/indicators |
| Профиль пользователя | `aisystant/user-profile-service` | API профиля |
| Контекст обучения | `aisystant/learning-context-service` | Контекст для агентов |
| Веб-интерфейс IWE | `TserenTserenov/iwe-guide-web` | iwe.aisystant.com |

### Инфраструктура

| Репо | GitHub | Назначение |
|------|--------|-----------|
| Миграции БД | `TserenTserenov/neon-migrations` | Единственный источник схемы Neon (ВСЕ 16 БД) |
| Реестр платежей | `TserenTserenov/payment-registry` | Журнал транзакций |
| Приём платежей | `aisystant/payment-receiver` | Stripe/YooKassa webhook (CF Worker) |
| Оповещения | `aisystant/observability-webhook` | Better Stack → Telegram (CF Worker) |
| Статус-страница | `aisystant/status-proxy` | status.aisystant.com (CF Worker) |
| Симулятор | `aisystant/simulator-lab` | Streamlit UI (Railway) |
| Прокси симулятора | `aisystant/simulator-proxy` | simulator.aisystant.com → Railway (CF Worker) |

### Шаблон и IWE

| Репо | GitHub | Назначение |
|------|--------|-----------|
| Шаблон рабочей среды | `TserenTserenov/FMT-exocortex-template` | IWE-шаблон для новых пользователей |
| Governance ИИ-систем | `TserenTserenov/DS-ai-systems` | Описание AI-систем в работе |

---

## Доступ в GitHub org

Все репо `aisystant/*` выдавать через **GitHub Team** в организации Aisystant (read для всей команды, write — по роли).

Репо `TserenTserenov/*` — личные репо пилота. Доступ выдаётся отдельно по запросу.

---

## Разграничение по роли в команде

| Роль | Обязательно клонировать локально |
|------|----------------------------------|
| Разработчик MCP | gateway-mcp, knowledge-mcp, event-gateway + нужный MCP-сервис |
| Разработчик бота | aist_bot, activity-hub, multi-domain-projection-worker |
| Разработчик фронтенда | iwe-guide-web, user-profile-service |
| Инфраструктура / БД | neon-migrations (обязательно всем кто меняет схему) |
| Все разработчики | DS-ecosystem-development + PACK-digital-platform через MCP |
