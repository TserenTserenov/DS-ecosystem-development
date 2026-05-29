---
title: "Инфраструктура хелпдеска IWE"
status: draft
created: 2026-05-29
wp_ref: WP-341
family: F7
owner: ops
---

# Инфраструктура хелпдеска IWE

> Описание текущего состояния и пути развития. Версия 0.1 (29 мая 2026).
> Артефакт WP-341. Обновлять при каждом изменении инфраструктуры.
>
> 📊 **Статус платформы для пользователей:** https://aisystant.betteruptime.com

<details open>
<summary><b>1. Карта сервисов</b></summary>

| Сервис | URL | Хостинг | Статус | Роль |
|--------|-----|---------|--------|------|
| **Chatwoot** | chatwoot-web-production-177b.up.railway.app | Railway / chatwoot-iwe | ✅ | Helpdesk-система: тикеты, ответы операторов |
| **n8n** | n8n-production-c098.up.railway.app | Railway / peaceful-vision | ✅ | Автоматизация: ДЗ-чекер, health probe |
| **BetterStack** | [aisystant.betteruptime.com](https://aisystant.betteruptime.com) | SaaS | ✅ | Внешний мониторинг + [статус-страница](https://aisystant.betteruptime.com) для пользователей |
| **guides-mcp** | guides-mcp.aisystant.workers.dev/mcp | Cloudflare Workers | ✅ | Семантический поиск по руководствам |
| **knowledge-mcp** | knowledge-mcp.aisystant.workers.dev/mcp | Cloudflare Workers | ✅ | Анализ вербализации, граф знаний |
| **digital-twin-mcp** | digital-twin-mcp.aisystant.workers.dev/mcp | Cloudflare Workers | ✅ | Цифровой двойник пользователя |
| **LLM Proxy** | (internal, Railway iwe-llm-proxy) | Railway | ✅ | Прокси запросов к Claude (Haiku/Sonnet) |
| **Neon DB (learning)** | ep-dark-hall-ag8bo8lf (EU Central) | Neon Serverless | ✅ | БД логов ДЗ-чекера, mcp_health_log |
| **Neon DB (chatwoot)** | ep-dark-hall-ag8bo8lf (EU Central) | Neon Serverless | ✅ | БД Chatwoot |
| **Railway Postgres** | postgres.railway.internal | Railway / peaceful-vision | ✅ | БД n8n |

</details>

<details>
<summary><b>2. Telegram-каналы</b></summary>

| Канал | Ссылка | Участников | Назначение | Алерты |
|-------|--------|-----------|-----------|--------|
| **Aisystant_status** | t.me/+2Tdn-M33vasyNzli | ~5 | Инциденты платформы: алерты BetterStack + mcp-health-probe | ✅ настроен |
| **Aisystant - feedback chat** | t.me/+5WH59nuwrnY3M2Ji | ~100 | Сообщения пользователей о работе платформы | ❌ не подключён к Chatwoot |
| **Helpdesk Aisystant** | t.me/+I2t97dfgL68xZmU6 | ? | Роль не определена → см. Roadmap Фаза B | ❌ нет алертов |

</details>

<details>
<summary><b>3. Мониторинг и алертинг</b></summary>

### Схема

```
Внешние               Внутренние             Каналы
─────────             ──────────             ──────
BetterStack ──────→  webhook/check ──────→  Aisystant_status
(каждые 3 мин)       keyword: "verdict"     (TG)

n8n health-probe ──→ guides-mcp ──────────→ Aisystant_status
(каждые 30 мин)      knowledge-mcp          (TG)
                     digital-twin-mcp
                     hw-checker-webhook

BetterStack ──────→  aisystant.betteruptime.com
                     (публичная статус-страница)
```

### BetterStack

- **Монитор:** `POST https://n8n-production-c098.up.railway.app/webhook/check`
- **Тип проверки:** keyword — `verdict` (присутствие в теле ответа)
- **Тело запроса:** `{"question_text":"Что такое системное мышление?","answer_text":"monitor-check","course_name":"monitor"}`
- **Частота:** каждые 3 минуты
- **Recovery period:** 3 минуты
- **Получатель алертов:** primary on-call → **Aisystant_status** (TG)
- **Статус-страница:** https://aisystant.betteruptime.com (публичная, для пользователей)

> ⚠️ BetterStack запускает полный LLM-пайплайн при каждой проверке (Claude Haiku).
> Стоимость: ~480 запросов/сутки к ДЗ-чекеру только от мониторинга.
> **TODO:** рассмотреть отдельный `/healthz` эндпоинт без LLM для внешнего мониторинга.

### mcp-health-probe (n8n, ID: OZe8hJBLlOwYahVk)

- **Запуск:** cron `*/30 * * * *` (каждые 30 мин)
- **Проверяет:**
  - `guides-mcp` — semantic_search, keyword: не задан (JSON error check)
  - `knowledge-mcp` — graph_stats
  - `digital-twin-mcp` — tools/list
  - `hw-checker-webhook` — POST /webhook/check, keyword: `"ok"` (keyword-check)
- **Алерт:** Telegram Bot → `-1003907065350` (**Aisystant_status**)
- **Логирование:** Neon learning DB → таблица `mcp_health_log`

</details>

<details>
<summary><b>4. n8n — Автоматизация</b></summary>

### ДЗ-чекер (hw-checker-v3, ID: FMuoh9mV2q8OpkVv)

- **Webhook:** `POST https://n8n-production-c098.up.railway.app/webhook/check`
- **Вход:** `{question_text, answer_text, task_id?, student_id?, course_name?}`
- **Пайплайн:**
  1. Validate Input (required fields check)
  2. Параллельно: `guides-mcp/semantic_search` + `knowledge-mcp/analyze_verbalization`
  3. Merge Results → Build Prompt
  4. AI Agent (Claude Haiku через LLM Proxy)
  5. Parse + Format → Respond to Webhook
  6. Log to Neon (`mcp_health_log`?)
- **Выход:** `{ok, verdict, score, strengths[], issues[], next_step, comment, concept_coverage, ...}`
- **SLA:** типичное время ответа ~10-15 сек (LLM round trip)

### Защита от переполнения диска (Railway Postgres)

> Инцидент 28 мая 2026: disk full → Postgres recovery loop → webhook 500/502 ~1 час.
> Root cause: workflow с `active: false` генерировал execution каждые 5 мин.

Текущие настройки:

| Переменная | Значение | Роль |
|-----------|---------|------|
| `EXECUTIONS_DATA_PRUNE` | `true` | Включает очистку |
| `EXECUTIONS_DATA_MAX_AGE` | `168` (7 суток) | Максимальный возраст execution |
| `EXECUTIONS_DATA_PRUNE_MAX_COUNT` | `25` | Лимит хранимых executions (жёсткий cap) |
| `EXECUTIONS_DATA_PRUNE_HARD_DELETE` | `true` | Физическое удаление (не soft-delete) |
| `EXECUTIONS_DATA_SAVE_ON_SUCCESS` | `none` | Не хранить успешные executions |

### Активные воркфлоу

| ID | Название | Статус | Расписание |
|----|---------|--------|-----------|
| FMuoh9mV2q8OpkVv | hw-checker-v3 | ✅ active | by webhook |
| OZe8hJBLlOwYahVk | mcp-health-probe | ✅ active | каждые 30 мин |

### Неактивные (исторические)

| ID | Название | Примечание |
|----|---------|-----------|
| e9z9m4tL77fxU45w | hw-checker-smoke-test | smoke-тест ДЗ-чекера |
| 29rZeWbpbby2IsFk | hw-checker-v3 copy | backup-копия |
| OYYPrwD7ya2uCb4L | ДЗ-чекер | v1 (legacy) |
| hVuTh8LDddIDKvvL | ДЗ-чекер v1.4 | legacy |
| oQKEEsJEFJv8g9Ox | ДЗ-чекер v1.2 | legacy |
| pRm0JWH6uiA9gwDh | ДЗ-чекер v1.3 | legacy |
| wiAZ9j6eg9mNVG2Z | ДЗ-чекер v2 | legacy |

> **TODO:** удалить legacy воркфлоу v1, v1.2, v1.3, v1.4, v2 и hw-checker-v3 copy.

</details>

<details>
<summary><b>5. Chatwoot — Helpdesk-система</b></summary>

- **URL:** https://chatwoot-web-production-177b.up.railway.app
- **Инсталляция:** IWE Helpdesk (community plan)
- **Хостинг:** Railway / chatwoot-iwe (отдельный проект)
- **Стек:** chatwoot-web + chatwoot-sidekiq (background jobs) + chatwoot-redis (queues)
- **БД:** Neon Serverless Postgres (EU Central)
- **Язык по умолчанию:** ru
- **Последний деплой:** 2026-05-20
- **Статус:** ✅ все 3 сервиса SUCCESS

### Текущее использование

> ⚠️ Chatwoot установлен, но **не интегрирован** с Telegram-группой пользователей (**Aisystant - feedback chat**).
> Сообщения пользователей из этой группы не попадают в тикеты Chatwoot.

</details>

<details>
<summary><b>6. Текущие проблемы и пробелы</b></summary>

| # | Проблема | Приоритет |
|---|---------|-----------|
| 1 | **Aisystant - feedback chat** (100 чел.) не подключён к Chatwoot — сообщения теряются | 🔴 высокий |
| 2 | **Helpdesk Aisystant** — роль не определена, алертов нет | 🟡 средний |
| 3 | BetterStack мониторит через полный LLM-пайплайн (дорого, ~480 req/сутки) — нет отдельного `/healthz` | 🟡 средний |
| 4 | Legacy воркфлоу (7 штук) засоряют n8n | 🟢 низкий |
| 5 | Нет disk usage alert для Railway Postgres (инцидент 28 мая) | 🟡 средний |
| 6 | Нет документации онбординга оператора Chatwoot | 🟡 средний |
| 7 | Нет runbook по инцидентам (что делать при 500/502 webhook) | 🟡 средний |

</details>

<details>
<summary><b>7. Roadmap развития</b></summary>

### Фаза A — Интеграция Telegram → Chatwoot (🔴 приоритет 1)

**Задача:** подключить группу **Aisystant - feedback chat** как inbox в Chatwoot.

**Как (Вариант 1 — бот в группе):**
1. BotFather → `/newbot` → создать бота (например, `@aisystant_support_bot`)
2. BotFather → `/setprivacy` → выбрать бота → `Disable` (иначе бот читает только @упоминания)
3. Chatwoot → Settings → Inboxes → New Inbox → **Telegram** → вставить токен бота
4. Добавить бота в группу **Aisystant - feedback chat** как участника

**Поведение:** каждый пользователь группы = отдельный тикет в Chatwoot. Оператор отвечает из Chatwoot → ответ появляется в группе от имени бота.

**Ограничение:** ответы оператора публичны в группе (не в личку). Если нужны личные ответы — Вариант 2 (n8n как посредник, извлекает `user_id` и шлёт DM).

**Результат:** все сообщения из группы 100 пользователей → тикеты Chatwoot → операторы отвечают из одного интерфейса.

### Фаза B — Определить роль канала **Helpdesk Aisystant**

**Варианты:**
- **Ops эскалация (уровень 2):** если primary (Aisystant_status) не ответил за 15 мин → алерт сюда
- **Dev-канал:** уведомления о деплоях, PR, технические события
- **Архивировать:** если группа неактивна — убрать из схемы

### Фаза C — Лёгкий `/healthz` эндпоинт ✅ Done (29 мая)

**Задача:** мониторинг n8n без LLM-вызовов за <100ms.

**Решение:** n8n имеет встроенный эндпоинт `GET /healthz` → `{"status":"ok"}` (HTTP 200).
Никакого воркфлоу не нужно — endpoint всегда доступен пока n8n жив.

**BetterStack переключить:**
- URL: `GET https://n8n-production-c098.up.railway.app/healthz`
- Keyword check: `"ok"`
- Убрать тело запроса (не нужно)

**Экономия:** ~480 req Haiku в сутки (~$0.10/день) → 0

**Примечание:** воркфлоу `healthz` (ID: xbT7EV6wZrkhPp9n) деактивирован — был попыткой решить ту же задачу, встроенный endpoint лучше.

**Результат:** BetterStack мониторит через встроенный `/healthz` (не тратит токены), mcp-health-probe продолжает мониторить полный пайплайн включая LLM.

### Фаза D — Disk alert для Railway Postgres

**Задача:** n8n workflow раз в час → Railway API (metrics) → если usage > 80% → алерт в Ops Telegram.

**Альтернатива:** BetterStack Heartbeat monitor — n8n шлёт heartbeat каждый час, BetterStack алертит если heartbeat пропал (означает: n8n не работает → Postgres не работает).

### Фаза E — Runbook и онбординг

**Задача:** создать в `DS-ecosystem-development/0.OPS/`:
- `0.9.Runbooks/helpdesk-incident-runbook.md` — шаги при инциденте (500/502/disk full)
- `0.9.Runbooks/chatwoot-operator-guide.md` — онбординг оператора поддержки

### Фаза F — Табло статуса платформы для пользователей

**Задача:** сделать публичную страницу статуса сервисов, доступную пользователям платформы — по аналогии с [status.claude.com](https://status.claude.com/).

**Текущее состояние:** страница https://aisystant.betteruptime.com уже существует (BetterStack), но не настроена под пользователей: нет компонентов, нет истории инцидентов, не опубликована.

**Что сделать:**
1. BetterStack → Status Pages → добавить компоненты: ДЗ-чекер, IWE, Бот, MCP-сервисы, Обучение
2. Настроить кастомный домен `status.aisystant.com` (CNAME → BetterStack)
3. Включить историю инцидентов (инцидент 28 мая — ретроспективно)
4. Опубликовать ссылку: в боте (`/status`), на сайте (footer), в FAQ

**Референс:** [status.claude.com](https://status.claude.com/) — каждый компонент со статусом + история инцидентов + подписка на уведомления.

**Результат:** пользователь сам проверяет статус платформы без запроса в поддержку. Уменьшает нагрузку на Chatwoot при инцидентах.

</details>

<details>
<summary><b>8. Зависимости</b></summary>

```
Пользователь → Aisystant - feedback chat → [TODO: Chatwoot inbox] → Chatwoot → Оператор
Пользователь → ДЗ-чекер webhook → n8n → guides-mcp + knowledge-mcp → Claude Haiku → Ответ
Оператор → Chatwoot → [TODO: reply bot] → Aisystant - feedback chat
Мониторинг → BetterStack → aisystant.betteruptime.com → Aisystant_status (TG)
Мониторинг → mcp-health-probe (n8n) → Neon log + Aisystant_status (TG)
```

</details>

---

*Создан: 2026-05-29. Следующий ревью: при изменении любого сервиса или при Week Close.*

---

## Осталось (сессия 2026-05-29, обновлено)

**Что сделано:** Фаза C закрыта — n8n встроенный `/healthz` работает без воркфлоу.

**Что дальше:**
- [ ] Переключить BetterStack монитор: с `POST /webhook/check` на `GET /healthz`, keyword: `"ok"`
- [ ] Фаза F: BetterStack status page — добавить компоненты, custom domain `status.aisystant.com`

**Следующий шаг:** переключить BetterStack монитор
