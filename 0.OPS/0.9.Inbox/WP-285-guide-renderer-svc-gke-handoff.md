---
type: handoff
status: draft
created: 2026-06-25
updated: 2026-06-25
owner: Андрей
next_review: 2026-07-09
related: [WP-285, WP-149, WP-415]
---

# Новая архитектура платформы — план GKE-деплоя

**Источник:** оперативка ИТ 23 июня 2026 (WP-285 Ф7 Часть Б).

20 сервисов платформы (не считая 15 Cloud SQL). Разделены на MCP-экосистему (отдельный файл) и остальные сервисы (ниже).

---

## 1. MCP-сервисы

Полный хэндофф: [WP-285-aisystant-mcp-gke-handoff.md](WP-285-aisystant-mcp-gke-handoff.md).

| Название | Назначение | Сервис | Тип деплоя |
|----------|-----------|--------|-----------|
| Шлюз API | Единственная точка входа: OAuth, маршрутизация, авторизация | gateway-mcp | CF Worker |
| Поиск по базе знаний | Поиск по Pack, гайдам, SOTA, графу концептов | knowledge-mcp | CF Worker |
| Личная база знаний | Личные заметки и эмбеддинги пользователя | personal-knowledge-mcp | CF Worker |
| Цифровой двойник | Показатели прогресса, CP-профиль, снапшоты ученика | digital-twin-mcp | CF Worker |
| Каталог руководств | Каталог программ обучения и руководств | guides-mcp | CF Worker |
| Конечный автомат | FSM-состояния ассистента ученика в диалоге | fsm-mcp | CF Worker |
| Google Drive | Python MCP-сервер: доступ к Google Drive пользователя | google-drive-mcp | GKE Deployment |
| Профиль пользователя | Контекст, тариф, BYOK-ключи, уведомления боту | user-profile-service | GKE Deployment |
| Контекст обучения | Согласие на данные, когнитивный бриф, онбординг | learning-context-service | GKE Deployment |
| Интеграция с GitHub | Вебхуки GitHub App, вход через GitHub, создание репо | github-integration-service | GKE Deployment |
| Статус агентов | Доска статусов агентов | agent-status-service | GKE Deployment |

> **Примечание:** guides-mcp, fsm-mcp и google-drive-mcp пока не включены в детальный handoff-файл.

---

## 2. Коммуникация

| Название | Назначение | Сервис | Тип деплоя | Dockerfile |
|----------|-----------|--------|-----------|------------|
| Telegram-бот | Основной интерфейс пользователя через Telegram | aist_bot_newarchitecture | GKE Deployment | есть |

---

## 3. Платежи

| Название | Назначение | Сервис | Тип деплоя | Dockerfile |
|----------|-----------|--------|-----------|------------|
| Приём платежей | Webhook от Stripe, запись входящих транзакций | payment-receiver | CF Worker | нет (wrangler) |
| Журнал транзакций | Encrypted-хранилище платёжных данных (Fernet column-level) | payment-registry | GKE Deployment | **нужен** |

---

## 4. Генератор персональных руководств

Пользователи с IWE генерируют руководство локально. Пользователи без IWE/Git получают его с платформы через этот сервис.

**Сервис:** guide-renderer-svc (новый) - GKE CronJob. **Расписание:** ежедневно 06:00 UTC.

**Фильтр:** только пилоты с `has_iwe_git=False`. Понедельник - полный прогон, вт-вс - только дневное руководство.

### Функции для переноса из `DS-autonomous-agents/scripts/`

| Название | Назначение | Функция в коде | Модуль |
|----------|-----------|---------------|--------|
| Загрузка пилотов | Читает список пилотов из learning и indicators БД | `load_pilots_from_db()` | `render-pilot-guides.py` |
| Профиль RCS | Определяет ступень и слабый слот пользователя | `get_rcs_profile()` + `_rcs_from_digital_twin()` | `render-pilot-guides.py` |
| Профиль CP | Читает CP-профиль из цифрового двойника | `get_cp_profile()` | `render-pilot-guides.py` |
| События активности | Собирает последние события пользователя | `get_recent_events()` | `render-pilot-guides.py` |
| Метрики активности | WakaTime, слоты, коммиты за период | `get_iwe_activity_metrics()` | `render-pilot-guides.py` |
| Активные задачи | Читает открытые рабочие задачи из GitHub пилота | `get_strategy_inputs()` + `_rank_wp_by_budget()` | `render-pilot-guides.py` |
| Рефлексии | Читает рефлексии пользователя из GitHub-репо | `get_pilot_reflections()` | `render-pilot-guides.py` |
| Сборка промпта | Формирует системный промпт с данными пилота | `_build_system_prompt_v2()` | `render-pilot-guides.py` |
| Генерация через Claude | Вызов Claude API, получение текста руководства | `generate_guide_v2()` | `render-pilot-guides.py` |
| Запись в GitHub | Сохраняет руководство в приватный репо пилота | `write_file()` + `generate_guide_json()` | `render-pilot-guides.py` |
| Архивирование | Переносит старые файлы в архив | `archive_old_weekly()` + `archive_old_daily()` | `render-pilot-guides.py` |
| Уведомление в Telegram | Отправляет пуш, дедуп - не чаще раза в день | `send_tg()` + `_guide_notified_today()` | `render-pilot-guides.py` |
| Рунг | Вычисляет рунг по ступени и МШС | `derive_rung()` | `program_dispatcher.py` |
| Поли-контекст | Собирает контекст по рунгу | `build_poly_context_by_rung()` | `program_dispatcher.py` |
| Контекст программы | Возвращает контекст программы ЛР/РР/ИР | `get_program_seed_context()` | `program_dispatcher.py` |
| Объём руководства | Определяет размер руководства по рунгу | `derive_volume_spec()` | `program_dispatcher.py` |
| Веса программ | Веса и ведущая программа по рунгу | `get_weights()` + `get_leading_program()` | `program_weights.py` |
| Выбор задания | Подбирает задание из каталога | `select_assignment()` | `assignment_selector.py` |
| Снапшот знаний | Предзагружает знания из knowledge-mcp в офлайн | `build_snapshot()` | `prefetch-knowledge-snapshot.py` |

### Переменные окружения

```env
ANTHROPIC_API_KEY=...
LEARNING_DB_URL=...
INDICATORS_DB_URL=...
TELEGRAM_BOT_TOKEN=...
GITHUB_APP_ID=...
GITHUB_APP_PRIVATE_KEY=...
```

### GitHub App

Права `contents: write` на `aisystant/*-guide` и `mim-school/*-guide`. Создаётся в рамках WP-415.

---

## 5. Backend / Инфра

| Название | Назначение | Сервис | Тип деплоя | Dockerfile |
|----------|-----------|--------|-----------|------------|
| Журнал событий | Единственный writer всех событий платформы | event-gateway | CF Worker | нет (wrangler) |
| Сборщик активности | Medallion ETL событий (bronze / silver / gold) | activity-hub | GKE Deployment | есть |
| Воркер проекций | Считывает события, строит проекции в persona / subscription / indicators | multi-domain-projection-worker | GKE CronJob | есть |
| Алерты наблюдаемости | Better Stack → Telegram-оповещения об инцидентах | observability-webhook | CF Worker | нет (wrangler) |
| Страница статуса | HTTP-редирект на status page платформы | status-proxy | CF Worker | нет (wrangler) |

---

## 6. Пробелы: что нужно создать

| Сервис | Что нужно | Приоритет |
|--------|-----------|-----------|
| **guide-renderer-svc** | Dockerfile + выделить функции из `DS-autonomous-agents/scripts/` | высокий |
| **payment-registry** | Dockerfile (сервис есть, контейнеризация не сделана) | средний |
| **google-drive-mcp** | Dockerfile (или порт в TypeScript CF Worker) | низкий |

---

## 7. Разграничение: Андрей vs Паша

| Зона | Андрей (разработчик) | Паша (DevOps) |
|------|---------------------|---------------|
| Dockerfile | Пишет для всех Python-сервисов | - |
| CF Workers | wrangler.toml + GitHub Action | - |
| Werf-манифест | Минимальный манифест (env, image, replicas) | Добавляет инфра-специфику |
| GKE кластер | - | Создаёт через Terraform |
| Cloud SQL | SQL-миграции | Создаёт инстанс, строку подключения |
| Секреты | Список env vars | K8s Secret, значения |
| Домены | Указывает потребность | DNS, SSL, Cloudflare rules |

---

## 8. Зависимости

| Зависимость | Статус | Что нужно |
|-------------|--------|-----------|
| GKE кластер (WP-285 Ф2) | prerequisite | Кластер для деплоя |
| GitHub App (WP-415) | pending | Права на запись в guide-репо |
| WP-149 Ф-platform-guide | pending | Детали формата «тайного гида» |

---

## Приложение А: по типу деплоя

### CF Workers (без MCP) - только env vars, wrangler.toml

| Название | Сервис | Что изменить для Track B |
|----------|--------|--------------------------|
| Журнал событий | event-gateway | Cloud SQL journal |
| Приём платежей | payment-receiver | Новый обработчик для Stripe webhooks |
| Алерты наблюдаемости | observability-webhook | Новый Telegram-бот для Track B |
| Страница статуса | status-proxy | Обновить CNAME на новый домен |

### GKE Deployments - Dockerfile + Werf

| Название | Сервис | Dockerfile |
|----------|--------|------------|
| Telegram-бот | aist_bot_newarchitecture | есть |
| Сборщик активности | activity-hub | есть |
| Журнал транзакций | payment-registry | **нужен** |

### GKE CronJobs - по расписанию

| Название | Сервис | Расписание | Dockerfile |
|----------|--------|-----------|------------|
| Воркер проекций | multi-domain-projection-worker | по расписанию | есть |
| Генератор руководств | guide-renderer-svc | 06:00 UTC ежедневно | **создаётся** |
