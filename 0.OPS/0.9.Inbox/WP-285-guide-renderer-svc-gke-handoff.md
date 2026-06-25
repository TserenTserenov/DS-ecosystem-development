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

**Источник:** Оперативка ИТ 23 июня 2026 (WP-285 Ф7 Часть Б).

Ниже перечислены все функции (сервисы) новой архитектуры платформы Track B с точки зрения Андрея как разработчика. Задача по каждой функции одинаковая: написать или актуализировать Dockerfile, подготовить Werf-манифест, передать Паше список env vars.

---

## 1. Веб-воркеры (CF Workers) — 10 функций

Все воркеры написаны на TypeScript, деплоятся через Cloudflare. Для Track B меняются только переменные окружения и имена (создаётся новый `wrangler.toml`).

| Название | Назначение | Репозиторий | Что изменить для Track B |
|----------|-----------|-------------|--------------------------|
| Шлюз API | Авторизация OAuth, маршрутизация по доменам, единственная точка входа для внешних клиентов | gateway-mcp | Обновить адреса 8 сервисов + ключ подписи; новый домен |
| Поиск по базе знаний | Полнотекстовый поиск по Pack, гайдам, SOTA, графу концептов | knowledge-mcp | Переключить на Cloud SQL knowledge; переиндексировать под EN-контент |
| Личная база знаний | Личные заметки и эмбеддинги пользователя, доступ через шлюз | personal-knowledge-mcp | Переключить на Cloud SQL persona |
| Цифровой двойник | Показатели прогресса, базовые оценки, снапшоты ученика | digital-twin-mcp | Переключить на Cloud SQL indicators |
| Каталог руководств | Каталог программ обучения и персональных руководств | guides-mcp | Переключить на Cloud SQL reference; загрузить EN-программы |
| Журнал событий | Единственная точка записи событий платформы | event-gateway | Переключить на Cloud SQL journal |
| Конечный автомат | FSM-состояния ассистента ученика | fsm-mcp | Переменные среды под Track B; stateless |
| Приём платежей | Webhook от Stripe (Track B — только Stripe, без ЮКассы) | payment-receiver | Новый обработчик для Stripe webhooks |
| Алерты наблюдаемости | Webhook от Better Stack → Telegram-оповещения об инцидентах | observability-webhook | Новый Telegram-бот для Track B |
| Страница статуса | HTTP-редирект на страницу статуса платформы | status-proxy | Обновить CNAME на новый домен |

---

## 2. Python-сервисы (GKE) — 6 функций

Сейчас 5 из 6 живут на Railway. Track B: GKE Standard (Kubernetes Deployment или CronJob). Dockerfile у 4 из 6 уже есть.

| Название | Назначение | Репозиторий | Тип в GKE | Dockerfile |
|----------|-----------|-------------|-----------|------------|
| Telegram-бот | Основной интерфейс пользователя через Telegram | aist_bot_newarchitecture | Deployment | есть |
| Воркер проекций | Считывает события из журнала, строит проекции в persona / subscription / indicators | multi-domain-projection-worker | CronJob | есть |
| Сборщик активности | Medallion-конвейер событий (bronze → silver → gold) | activity-hub | Deployment | есть |
| Журнал транзакций | Единый журнал платёжных операций с шифрованием на уровне колонок (Fernet) | payment-registry | Deployment | **нет — нужен Dockerfile** |
| Интеграция Google Drive | Python MCP-сервер для доступа к Google Drive | google-drive-mcp | Deployment | **нет — нужен Dockerfile или порт в TypeScript** |
| **Генератор руководств** | Генерирует персональное руководство для пользователей без IWE/Git и записывает в приватный GitHub-репо | guide-renderer-svc **(новый)** | CronJob | **нет — создаётся** |

---

## 3. Детали нового сервиса: Генератор персональных руководств

Пользователи с IWE генерируют руководство локально на своей машине. Пользователи без IWE/Git получают его с платформы через этот сервис.

**Расписание:** ежедневно 06:00 UTC. Понедельник — полный прогон (еженедельное + дневное). Вт–вс — только дневное.

**Фильтр:** обрабатывать только пилотов с `has_iwe_git=False`.

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
| Уведомление в Telegram | Отправляет пуш, дедуп — не чаще раза в день | `send_tg()` + `_guide_notified_today()` | `render-pilot-guides.py` |
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
LEARNING_DB_URL=...           # БД обучения
INDICATORS_DB_URL=...         # БД показателей
TELEGRAM_BOT_TOKEN=...        # Бот для уведомлений
GITHUB_APP_ID=...
GITHUB_APP_PRIVATE_KEY=...
```

### GitHub App

Права `contents: write` на:
- `aisystant/*-guide` — мировой контур
- `mim-school/*-guide` — российский контур

Создаётся в рамках WP-415. Если WP-415 ещё не готов — отдельный App с минимальными правами.

---

## 4. Разграничение: Андрей vs Паша

| Зона | Андрей (разработчик) | Паша (DevOps) |
|------|---------------------|---------------|
| Dockerfile | Пишет для всех Python-сервисов | — |
| CF Workers | wrangler.toml + GitHub Action → Cloudflare | — |
| Werf-манифест | Минимальный манифест (env, image, replicas) | Добавляет инфра-специфику |
| GKE кластер | — | Создаёт через Terraform |
| Cloud SQL | Пишет SQL-миграции | Создаёт инстанс, выдаёт строку подключения |
| Секреты | Передаёт список env vars | Создаёт K8s Secret, заполняет значения |
| Домены | Указывает, какой сервис нуждается в домене | DNS, SSL, Cloudflare rules |

---

## 5. Зависимости

| Зависимость | Статус | Что нужно |
|-------------|--------|-----------|
| GKE кластер (WP-285 Ф2) | prerequisite | Кластер для деплоя |
| GitHub App (WP-415) | pending | Права на запись в guide-репо |
| WP-149 Ф-platform-guide | pending | Детали формата «тайного гида» |

---

## 6. Следующий шаг

1. Андрей подтверждает план или уточняет приоритет сервисов.
2. Церен создаёт Dockerfile для `guide-renderer-svc` в `DS-autonomous-agents`.
3. Паша разворачивает GKE CronJob после готовности GitHub App.
