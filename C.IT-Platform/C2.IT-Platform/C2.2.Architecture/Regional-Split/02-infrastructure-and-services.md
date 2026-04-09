---
family: F5
kernel: C
system: C2
role: Architecture
status: draft
created: 2026-04-09
depends_on: [WP-215, WP-187, WP-109, WP-73, WP-212]
source: "ИТ-встреча 5 (9 апр 2026), исследование паттернов"
---

# Инфраструктура и сервисы: архитектура двух контуров

> **Контекст:** Техническая инфраструктура дублируется по контурам. Общий слой (Community Layer) — единый.
> **Решения встречи:** Neon пока одна (EU). CRM = отдельный сервис. Два бота = два экземпляра одного кода.
> **Связь:** WP-73 (архитектура), WP-187 (Ory), WP-109 (Activity Hub), WP-212 (безопасность).

---

<details open>
<summary><b>1. Карта сервисов: что дублируется, что общее</b></summary>

```
КОНТУР «РОССИЯ»                                    КОНТУР «МИР»
┌────────────────────────────┐           ┌────────────────────────────┐
│                            │           │                            │
│  Бот @aist_ru              │           │  Бот @aist_me              │
│  Ory (self-hosted, РФ)     │           │  Ory Cloud (EU)            │
│  CRM-RU (оплаты, подписки) │           │  CRM-EU (оплаты, подписки) │
│  ЮKassa / Мир              │           │  Stripe / PayPal           │
│  PG-RU (или Neon-RU)       │           │  Neon EU                   │
│                            │           │                            │
│  [Сервер: Selectel / VPS]  │           │  [Сервер: Railway / Fly]   │
│                            │           │                            │
└──────────────┬─────────────┘           └──────────────┬─────────────┘
               │                                        │
               │ ingest_event (source_region='ru')       │ ingest_event (source_region='world')
               │                                        │
               └────────────────┬───────────────────────┘
                                │
                   ┌────────────▼────────────┐
                   │   COMMUNITY LAYER        │
                   │                          │
                   │  Activity Hub (WP-109)   │  ← агрегация событий
                   │  Points Engine (WP-121)  │  ← единые баллы
                   │  Knowledge MCP           │  ← общие знания
                   │  ЦД (digital twin)       │  ← единый профиль
                   │  Контент (курсы)         │  ← общие материалы
                   │                          │
                   │  [Где хостить: Neon EU]   │  ← псевдонимизированные данные
                   └──────────────────────────┘
```

### Сводка по сервисам

| Сервис | Дублируется? | Почему | Как связываются |
|--------|-------------|--------|-----------------|
| **Бот (Telegram)** | Да | Разные backend-конфиги, разные webhook URL | Один код, разные env vars |
| **Ory** | Да | PII в юрисдикции пользователя (152-ФЗ / GDPR) | Identity federation (canonical_ory_id) |
| **CRM-сервис** | Да | Разные платёжные шлюзы, разные юрлица | Пишут в один или два Neon через source_region |
| **Платёжный шлюз** | Да | ЮKassa ≠ Stripe, разные API, валюты | Полная изоляция |
| **БД (Neon/PG)** | Решить | PII в контуре, community data — общая | См. варианты ниже (§2) |
| **Activity Hub** | Нет | Единый поток событий, source_region | Один инстанс, принимает из обоих контуров |
| **Points Engine** | Нет | Баллы = общие (решение встречи) | Один инстанс |
| **Knowledge MCP** | Нет | Знания не имеют гражданства | Один инстанс |
| **ЦД** | Нет | Один человек = один ЦД | Привязка к canonical_ory_id |
| **Langfuse** | Нет | Observability не требует юрисдикции | Cloud или self-hosted |

</details>

<details>
<summary><b>2. Три варианта разделения данных</b></summary>

### 2.1. Вариант A: Одна Neon EU + PII в контурах (рекомендуемый на старте)

```
КОНТУР РФ                    COMMUNITY (Neon EU)           КОНТУР МИР
┌────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│ Ory-RU         │     │ user_events           │     │ Ory-EU         │
│ ory_id → ФИО   │     │ point_transactions    │     │ ory_id → ФИО   │
│ ory_id → email │     │ point_balances        │     │ ory_id → email │
│ ory_id → тел.  │     │ digital_twin_state    │     │ ory_id → адрес │
│ payments_ru    │     │ knowledge embeddings  │     │ payments_eu    │
│ (PII, 152-ФЗ)  │     │ (псевдоним по ory_id) │     │ (PII, GDPR)    │
└────────────────┘     └──────────────────────┘     └────────────────┘
```

- **PII** (ФИО, email, телефон) -- в Ory контура (где юрисдикция пользователя)
- **Community data** (события, баллы, ЦД) -- псевдонимизировано по ory_id, хранится в Neon EU
- **Юридическое обоснование:** псевдонимизированные данные не являются ПД по GDPR (Recital 26), если ключ деанонимизации (ory_id → ФИО) хранится отдельно (в контурном Ory). Для 152-ФЗ -- спорнее, но Роскомнадзор штрафует за хранение ПД, а ory_id без контекста = не ПД.

| + | - |
|---|---|
| Простота: одна БД, один Points Engine | Зависимость от канала РФ → Neon EU |
| Нет проблем с consistency | Если Роскомнадзор потребует — надо переезжать |
| Один source-of-truth для community | |

### 2.2. Вариант B: Neon EU + PG-RU + CDC

```
КОНТУР РФ                              КОНТУР МИР
┌──────────────────┐                   ┌──────────────────┐
│ PG-RU (Selectel)  │ ◄──── CDC ────► │ Neon EU            │
│ user_events (RU)  │                  │ user_events (all)  │
│ point_txns (RU)   │                  │ point_txns (all)   │
│ payments_ru       │                  │ payments_eu        │
│ Ory-RU             │                  │ Ory-EU             │
└──────────────────┘                   └──────────────────┘
```

- RU-контур автономен при недоступности EU
- CDC (Change Data Capture) синхронизирует события RU → EU
- Points Engine в EU агрегирует из обоих источников

| + | - |
|---|---|
| Автономность контуров | CDC — сложность, eventual consistency |
| Нет зависимости от канала | Конфликты при сверке |
| 152-ФЗ: все данные РФ в РФ | Двойные миграции, двойной мониторинг |

### 2.3. Вариант C: Community Layer как отдельный сервис (целевой)

```
КОНТУР РФ           COMMUNITY LAYER           КОНТУР МИР
┌───────────┐     ┌──────────────────┐     ┌───────────┐
│ PII + fin  │     │ Community DB      │     │ PII + fin  │
│ Ory-RU    │     │ Points Engine     │     │ Ory-EU    │
│ CRM-RU    │     │ ЦД               │     │ CRM-EU    │
│ PG-RU     │     │ Knowledge        │     │ Neon-EU   │
└─────┬─────┘     │ Content index    │     └─────┬─────┘
      │           └────────┬─────────┘           │
      │   events           │ API            events│
      └────────────────────┴─────────────────────┘
```

Community Layer = API-сервис с собственной БД. Контуры взаимодействуют через API, не через общие таблицы. Масштабируется на N контуров.

| + | - |
|---|---|
| Чистое разделение responsibilities | Дополнительный инфраслой |
| API-контракты, не shared DB | Нужен на масштабе, не сейчас |
| Юридически прозрачно | |
| N контуров без изменений | |

### Рекомендация: эволюция A → C

| Этап | Вариант | Триггер перехода |
|------|---------|------------------|
| **Сейчас** | **A** — одна Neon EU | -- |
| **При проблемах связности** | A + outbox в RU | Neon недоступна из РФ >1% |
| **При масштабе** | **C** — Community Layer API | 500+ активных, или юрид. требование |

**Не рекомендуется вариант B** (CDC между двумя полными БД) -- сложность федерации финансово-подобных данных не оправдана. Лучше сразу Community Layer (C).

</details>

<details>
<summary><b>3. Identity Federation: два Ory</b></summary>

### Проблема

Два инстанса Ory = два identity store. У одного человека -- два ory_id.

### Решение: canonical_ory_id + identity_links

```sql
CREATE TABLE identity_links (
    canonical_ory_id UUID PRIMARY KEY,  -- "главный" ID (из первого Ory)
    ory_id_ru UUID,                      -- ID в Ory-RU
    ory_id_eu UUID,                      -- ID в Ory-EU
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

- При регистрации в контуре: создаётся identity в контурном Ory + запись в identity_links
- Community Layer использует canonical_ory_id для всех операций
- Контурные сервисы используют контурный ory_id

### Когда это нужно

**Пока Ory одна (EU)** -- проблемы нет. Identity_links нужна при появлении Ory-RU. Закладываем в архитектуру сейчас (поле canonical_ory_id), реализуем при потребности.

</details>

<details>
<summary><b>4. Связность контуров: мониторинг и байпас</b></summary>

### Риски

| Риск | Вероятность | Последствие | Митигация |
|------|------------|-------------|-----------|
| Блокировка Neon из РФ | Средняя | CRM-RU не пишет, баллы не начисляются | Outbox + retry, PG-RU как буфер |
| Замедление канала РФ → EU | Высокая | Задержки в отображении баллов | Кэш, async, eventual consistency ок |
| Блокировка Railway | Низкая | Бот-мир недоступен из РФ (ок — это бот для мира) | -- |
| Блокировка Telegram API из РФ | Низкая (прецедент 2018) | Оба бота недоступны | Webhook через прокси |

### Outbox-паттерн для RU-контура

```
Событие в RU → Outbox (PG-RU) → Retry worker → Neon EU
                                     │
                     при недоступности: backlog
                     при восстановлении: flush
```

Без outbox: событие теряется при недоступности Neon. С outbox: eventual delivery, баллы начисляются с задержкой (часы/дни), что допустимо для нефинансовых метрик.

### Мониторинг

| Метрика | Источник | Алерт |
|---------|----------|-------|
| Latency PG-RU → Neon EU | healthcheck endpoint | >500ms P95 |
| Outbox queue length | PG-RU | >100 events |
| Sync lag (events) | count diff | >1000 или >24h |
| Ory-RU availability | healthcheck | downtime >5min |

</details>

<details>
<summary><b>5. Деплой: где что работает</b></summary>

### Текущая инфраструктура (один контур)

| Сервис | Где | Провайдер |
|--------|-----|-----------|
| Бот (@aist_me) | Railway | peaceful-vision |
| Neon | EU (Frankfurt) | Neon Cloud |
| Ory | EU | Ory Cloud |
| Knowledge MCP | Railway | -- |
| Langfuse | Cloud | Langfuse Cloud |

### Целевая (два контура)

| Сервис | Контур РФ | Контур мир |
|--------|-----------|------------|
| **Бот** | Selectel / VPS (РФ) | Railway |
| **Ory** | Self-hosted (Selectel) | Ory Cloud (EU) |
| **CRM** | Selectel (→ PG-RU) | Railway (→ Neon EU) |
| **PG/Neon** | PG на Selectel (PII+outbox) | Neon EU (community + мир-PII) |
| **Activity Hub** | -- | Railway (единый) |
| **Points Engine** | -- | Railway (единый) |
| **Knowledge MCP** | -- | Railway (единый) |
| **Langfuse** | -- | Cloud (единый) |

**RU-сервер:** обсудить с Андреем 13 апр (WP-73). Его платформа = для AI-агентов. Бот, CRM, Ory = не AI-агенты, нужен отдельный VPS.

</details>

<details>
<summary><b>6. Чеклист «что заложить сейчас» (Вариант A)</b></summary>

| Что | Зачем | Статус |
|-----|-------|--------|
| `source_region` в point_transactions | Аудит: откуда событие. Готовность к разделению | Заложено в схеме (WP-121) |
| `source_region` в user_events | Трассировка источника | В WP-109 |
| Outbox-паттерн в RU-адаптерах | Устойчивость при недоступности Neon | Проектируется |
| `canonical_ory_id` в identity_links | Готовность к двум Ory | Спроектировано, не реализовано |
| Healthcheck endpoint Neon из РФ | Мониторинг связности | TODO |
| env-based конфигурация бота | Один код, два экземпляра | Частично (derive_mode) |

</details>

---

*Создано: 2026-04-09. WP: 215, 187, 109, 73, 212. Источник: ИТ-встреча 5, архитектурный анализ, исследование паттернов (GitLab Geo, Matrix federation, Telegram infra).*
