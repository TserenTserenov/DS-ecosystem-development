---
id: DP.CONCEPT.004
title: "Концепция прямых платежей: от монолита к платформе"
status: draft
created: 2026-04-16
wp: 246
author: Церен Церенов
related: [DP.ARCH.004, DP.SC.112, WP-183, WP-231, WP-228, WP-73]
---

# Концепция прямых платежей: от монолита к платформе

> **Контекст:** Aisystant — монолит, обрабатывающий платежи каналов 1–5. Переход на новую архитектуру: все 8 каналов пишут в Neon напрямую, Aisystant перестаёт быть посредником для новых оплат.

---

<details open>
<summary><b>§1. Проблема и мотивация</b></summary>

## Текущее состояние (AS-IS)

```
┌─────────────────────────────────────────────────────────┐
│                    Aisystant (монолит)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ YooKassa │  │ Paybox   │  │ Stripe   │  │ Tilda   │ │
│  │ ch1,4,6  │  │ ch2      │  │ ch3      │  │ ch5     │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       └──────┬───────┴─────────────┴─────────────┘      │
│              ▼                                           │
│     Aisystant PG (source of truth ch1-5)                │
│              │                                           │
└──────────────┼───────────────────────────────────────────┘
               │ pull каждые 10 мин (incremental-sync GHA)
               ▼
┌──────────────────────────────────────────────────────────┐
│            Neon (platform)                                │
│  ┌─────────────────┐  ┌──────────────────┐               │
│  │ finance_payments │  │ subscription_    │               │
│  │ (проекция ch1-5  │  │ grants           │               │
│  │  + прямая ch6-8) │  │ (из sync каж.    │               │
│  └─────────────────┘  │  30 мин)          │               │
│                        └──────────────────┘               │
│  ┌────────────┐   ┌──────────┐   ┌────────────────┐      │
│  │ Бот ch6,7  │   │ Directus │   │ Gateway MCP    │      │
│  │ (прямая    │   │ ch8 ручн.│   │ (читает grants)│      │
│  │  запись)   │   │          │   │                │      │
│  └────────────┘   └──────────┘   └────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

### Проблемы

| # | Проблема | Следствие |
|---|----------|-----------|
| 1 | **Aisystant — single point of failure** для ch1–5 | Если Aisystant упал — платежи принимаются, но не попадают в Neon до восстановления |
| 2 | **Задержка 10–40 мин** (cron sync) | Пользователь оплатил, но Gateway ещё не видит подписку |
| 3 | **Нет новых каналов без Димы** | Добавление канала требует изменений в Java-монолите |
| 4 | **Дублирование логики** | Бот (ch6–7) уже пишет напрямую в Neon, а ch1–5 идут через Aisystant — два разных потока данных |
| 5 | **Identity gap** | ch1–5 через LMS знают email/suser_id, ch6–7 знают только telegram_id — разрыв в identity при reconciliation |
| 6 | **Невозможна real-time аналитика** | Metabase видит данные с задержкой sync |

### Целевое состояние (TO-BE)

```
┌─────────────────────────────────────────────────────────┐
│              Payment Receiver (Cloudflare Worker)         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ YooKassa │  │ Paybox   │  │ Stripe   │  │ Tilda   │ │
│  │ webhook  │  │ webhook  │  │ webhook  │  │ webhook │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       └──────┬───────┴─────────────┴─────────────┘      │
│              ▼                                           │
│     verify → normalize → idempotent write → respond 200 │
└──────────────┼───────────────────────────────────────────┘
               │ прямая запись (< 1 сек)
               ▼
┌──────────────────────────────────────────────────────────┐
│            Neon (platform) — единый реестр                │
│  ┌─────────────────┐  ┌──────────────────┐               │
│  │ finance_payments │  │ subscription_    │               │
│  │ (все 8 каналов   │  │ grants           │               │
│  │  напрямую)       │  │ (trigger или     │               │
│  └─────────────────┘  │  cron < 1 мин)   │               │
│                        └──────────────────┘               │
│  ┌────────────┐   ┌──────────┐   ┌────────────────┐      │
│  │ Бот ch6,7  │   │ Directus │   │ Gateway MCP    │      │
│  │ Stars      │   │ ch8 B2B  │   │ (real-time)    │      │
│  └────────────┘   └──────────┘   └────────────────┘      │
│                                                          │
│  ┌─────────────────────────────────────────────┐         │
│  │ Aisystant (legacy read-only проекция ←──────│──── Reconciliation sync │
│  └─────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────┘
```

</details>

---

<details>
<summary><b>§2. Исследование мирового опыта (SOTA)</b></summary>

## 2.1. Payment Orchestration Layer

Современные платёжные платформы (Stripe, Adyen, Square) используют **Payment Orchestration Layer** — промежуточный слой между бизнес-логикой и провайдерами:

| Компонент | Назначение | Наш аналог |
|-----------|-----------|------------|
| **API Gateway** | Аутентификация, rate limiting | Gateway MCP (уже есть) |
| **Orchestration Core** | Маршрутизация, fallback | Payment Receiver (новый) |
| **PSP Connectors** | Адаптеры к провайдерам | YooKassa/Stripe/Paybox адаптеры |
| **Ledger** | Двойная запись, immutable log | finance_payments + audit.log |
| **Event Publisher** | Async уведомления | subscription_grants trigger/cron |

**Источники:** [Payment Orchestration Engine Architecture](https://www.craftingsoftware.com/payment-orchestration-engine-architecture-advanced-implementation-strategies), [Design a Payment System](https://www.systemdesignhandbook.com/guides/design-a-payment-system/)

## 2.2. Webhook-First Architecture

Индустриальный стандарт: **async-first API design** — POST для создания платежа, webhook для уведомления о результате.

**Ключевые паттерны:**

1. **Outbox Pattern** — событие записывается в БД в одной транзакции с платежом, background worker публикует дальше. Гарантирует at-least-once delivery без потери событий.

2. **Idempotency** — каждый webhook обрабатывается ровно один раз:
   - Таблица `processed_webhooks (event_id TEXT PRIMARY KEY)`
   - INSERT event_id → обработка → при дубле: UNIQUE violation → skip
   - TTL > retry window провайдера (YooKassa: 24h, Stripe: 72h)

3. **Signature Verification** — Stripe: HMAC-SHA256 подпись. YooKassa: проверка по IP-диапазонам + статус объекта через GET API.

4. **Respond First, Process Later** — вернуть HTTP 200 сразу, обработать асинхронно. Для Cloudflare Workers: `ctx.waitUntil()`.

**Источники:** [Stripe Idempotency](https://stripe.com/blog/idempotency), [Webhooks at Scale](https://hookdeck.com/blog/webhooks-at-scale), [Webhook Idempotency](https://hookdeck.com/webhooks/guides/implement-webhook-idempotency), [Stripe Webhooks Best Practices](https://www.stigg.io/blog-posts/best-practices-i-wish-we-knew-when-integrating-stripe-webhooks)

## 2.3. Strangler Fig для миграции от монолита

Паттерн: не переписывать монолит, а постепенно перенаправлять трафик.

| Фаза | Действие | Наш контекст |
|------|----------|-------------|
| **Shadow** | Новая система получает копию трафика, но не влияет на prod | incremental-sync (WP-183) уже это делает |
| **Canary** | 5%→25%→50%→100% трафика на новую систему | Начать с ch6 (бот ЮКасса) — единственный канал, где мы контролируем webhook URL |
| **Cutover** | Полное переключение | ch1–5 после координации с Димой |
| **Decommission** | Legacy в read-only | incremental-sync → archive-only |

**Anti-Corruption Layer**: Payment Receiver нормализует данные из разных провайдеров в единый формат `finance_payments`, изолируя внутреннюю модель от внешних API.

**Источники:** [Monolith to Microservices](https://circleci.com/blog/monolith-to-microservices-migration-strategies/), [Strangler Fig Pattern](https://www.griddynamics.com/blog/monolith-to-microservices)

## 2.4. Reconciliation

**Ежедневная сверка** — сравнение внутреннего ledger с отчётами провайдеров:
- Пропущенные webhook → GET API recovery
- Расхождение сумм → remediation queue
- Reconciliation = safety net, не основной поток

В нашем случае: на переходном этапе — reconciliation между Aisystant PG и Neon finance_payments (уже есть как incremental-sync). На целевом — reconciliation между PSP reports и finance_payments.

## 2.5. Cloudflare Workers для webhook-приёмника

Cloudflare Workers — подходящая платформа для webhook receiver:
- `ctx.waitUntil()` для async обработки после HTTP 200
- Web Crypto API для HMAC signature verification (Stripe)
- `@neondatabase/serverless` (neon()) для HTTP-based запросов к Neon (уже используется в gateway-mcp)
- Cloudflare Workflows (GA) для durable execution при сложной логике
- Cloudflare Queues для буферизации при пиковых нагрузках

**Наш опыт:** gateway-mcp уже работает как Cloudflare Worker с Neon через `@neondatabase/serverless`. Инфраструктура знакомая.

**Источники:** [Stripe SDK in Workers](https://blog.cloudflare.com/announcing-stripe-support-in-workers/), [Cloudflare Workflows GA](https://blog.cloudflare.com/workflows-ga-production-ready-durable-execution/), [Webhooks in Cloudflare](https://hookdeck.com/webhooks/platforms/how-to-receive-and-replay-external-webhooks-in-cloudflare-with-hookdeck)

## 2.6. Специфика провайдеров

### YooKassa (ch1, ch4, ch6)
- **Retry:** 24 часа
- **Верификация:** IP-диапазоны (185.71.76.0/27 и др.) + GET подтверждение статуса
- **Формат:** JSON `{type, event, object}`
- **Endpoint:** HTTPS :443/:8443, TLS 1.2+
- **Ответ:** HTTP 200 (тело игнорируется)

### Stripe (ch3)
- **Retry:** 72 часа (3 дня)
- **Верификация:** HMAC-SHA256 signature (`Stripe-Signature` header)
- **Формат:** Event object с `data.object`
- **Ответ:** HTTP 2xx в течение 20 секунд
- **Идемпотентность:** `event.id` уникален

### Telegram Stars (ch7)
- **Не webhook в классическом смысле** — Bot API `pre_checkout_query` + `successful_payment`
- **Подписки:** `subscription_period` параметр в `createInvoiceLink`
- **Верификация:** Telegram Bot API встроенная
- **Уже реализовано в боте:** WP-231 Ф-H

### Paybox (ch2)
- Webhook URL настраивается в личном кабинете
- Верификация по подписи (аналогично YooKassa)

### Tilda/Ecwid (ch5)
- Webhook при оплате через витрину
- Посредник — Aisystant обрабатывает оплату, мы получаем через sync

</details>

---

<details>
<summary><b>§3. Архитектурные принципы</b></summary>

## П1. Neon = единственный реестр платежей (Single Source of Truth)

Все 8 каналов оплаты пишут в `finance_payments` (Neon, база `platform`). Aisystant перестаёт быть промежуточным хранилищем для наших нужд.

## П2. Producer не знает о consumer

Aisystant (producer) не должен знать о Payment Receiver (consumer). Webhook — это **push от провайдера** (YooKassa, Stripe), а не от Aisystant. Aisystant остаётся producer для своей БД, мы перехватываем уведомления от провайдера.

**Уточнение к WP-183:** `incremental-sync` (pull от Aisystant) — переходный механизм. Целевой — получение webhook напрямую от провайдера. Но для ch1 (YooKassa через Aisystant) потребуется координация с Димой: кто получает webhook первым? Варианты:

| Вариант | Описание | Pros | Cons |
|---------|---------|------|------|
| **A. Fan-out** | YooKassa шлёт webhook и Aisystant, и нам | Параллельно, без зависимости | YooKassa не поддерживает multiple endpoints для одного события |
| **B. Мы первые** | Webhook → Payment Receiver → notify Aisystant | Real-time, мы контролируем | Aisystant зависит от нас (инверсия зависимости) |
| **C. Aisystant первый** | Webhook → Aisystant → outbox event → мы | Минимум изменений у Димы | Зависимость от монолита, задержка |
| **D. Webhook + sync** | Webhook → нам. Aisystant → sync для legacy | Независимость | Два потока данных переходный период |

**Рекомендация: Вариант D** — webhook напрямую для новых оплат, sync для legacy/reconciliation. Переходный период: оба потока параллельно, reconciliation ловит расхождения.

## П3. Idempotent write (at-least-once + dedup)

Каждый webhook обрабатывается **at most once**:
```sql
CREATE TABLE processed_webhooks (
    event_id    TEXT PRIMARY KEY,
    provider    TEXT NOT NULL,        -- 'yookassa' | 'stripe' | 'paybox' | 'tilda'
    received_at TIMESTAMPTZ DEFAULT now(),
    processed   BOOLEAN DEFAULT false
);
```
Порядок: INSERT event_id → обработка → UPDATE processed=true. При дубле: UNIQUE violation → HTTP 200, skip.

## П4. Verify → Normalize → Write → Respond

Каждый webhook проходит 4 стадии:

1. **Verify** — проверка подлинности (IP для YooKassa, signature для Stripe)
2. **Normalize** — приведение к единой модели `finance_payments` (Anti-Corruption Layer)
3. **Write** — идемпотентная запись в Neon
4. **Respond** — HTTP 200 (< 1 сек)

## П5. Fail closed для безопасности, fail open для доступности

- **Безопасность:** невалидный webhook → reject (HTTP 403). Невалидная подпись → reject.
- **Доступность:** если Neon недоступен → HTTP 500, провайдер retry через свой backoff.
- **subscription_grants:** fail closed (нет записи → нет доступа). Уже реализовано в Gateway (WP-231).

## П6. Strangler Fig — постепенная миграция

Не big bang. Каналы переключаются по одному. Legacy sync остаётся как reconciliation.

| Волна | Каналы | Причина |
|-------|--------|---------|
| **Волна 0 (уже)** | ch6, ch7, ch8 | Бот и Directus уже пишут напрямую |
| **Волна 1** | ch6 (ЮКасса-бот) | Мы контролируем webhook URL в боте |
| **Волна 2** | ch3 (Stripe) | Corp, отдельный аккаунт, webhook URL настраивается нами |
| **Волна 3** | ch1, ch2, ch4, ch5 | Требует координации с Димой (смена webhook URL или fan-out) |

## П7. Audit trail обязателен

Финансовые данные требуют полного журнала:
- `processed_webhooks` — что получили
- `finance_payments` — что записали
- `audit.log` — кто изменил (trigger на UPDATE/DELETE)
- PII Gate (B7.3): email, telegram_id — персональные данные, Security Gate обязателен

</details>

---

<details>
<summary><b>§4. Компоненты системы</b></summary>

## 4.1. Payment Receiver (новый компонент)

**Тип:** Cloudflare Worker (serverless)
**Репо:** `DS-MCP/payment-receiver/` (новый)
**Runtime:** Cloudflare Workers (TypeScript)
**Библиотеки:** `@neondatabase/serverless`, `stripe` (для signature verification)

### Ответственность

1. Принимает webhook от провайдеров (YooKassa, Stripe, Paybox, Tilda)
2. Верифицирует подлинность (IP/signature)
3. Нормализует в формат `finance_payments`
4. Идемпотентно записывает в Neon
5. Возвращает HTTP 200

### Маршрутизация

```
POST /webhook/yookassa   → YooKassaHandler
POST /webhook/stripe     → StripeHandler
POST /webhook/paybox     → PayboxHandler
POST /webhook/tilda      → TildaHandler
GET  /health             → HealthCheck
```

### Нормализация (Anti-Corruption Layer)

Каждый провайдер имеет свой формат. Payment Receiver нормализует в единую модель:

```typescript
interface NormalizedPayment {
  source_id: string;        // ID платежа у провайдера
  source_table: 'payment';
  source_system: string;    // 'yookassa' | 'stripe' | 'paybox' | 'tilda'
  channel: number;          // 1-8
  amount: number;
  currency: 'RUB' | 'USD' | 'EUR';
  purpose: 'SUBSCRIPTION' | 'INTERNSHIP' | 'WORKSHOP' | 'DONATION';
  success: boolean;
  email?: string;
  telegram_id?: bigint;
  ory_id?: string;
  suser_id?: number;
  payment_system: string;
  timestamp: Date;          // UTC
  charged_off_at?: Date;    // если сразу закрытый
  raw_payload: object;      // оригинальный webhook для audit
}
```

## 4.2. Существующие компоненты (без изменений)

| Компонент | Роль в новой архитектуре |
|-----------|------------------------|
| **finance_payments** (Neon) | Единый реестр — без изменений |
| **subscription_grants** (Neon) | Единый реестр подписок — без изменений |
| **Gateway MCP** (CF Worker) | Читает subscription_grants — без изменений |
| **Бот** (Railway) | Пишет ch6, ch7 напрямую — без изменений |
| **Directus** (Railway) | ch8 ручной ввод — без изменений |
| **Metabase** (Railway) | Аналитика — без изменений, но теперь real-time |

## 4.3. Компоненты на переходном этапе

| Компонент | Текущая роль | Переходная роль | Целевая роль |
|-----------|-------------|-----------------|-------------|
| **incremental-sync** (GHA cron) | Основной поток ch1–5 | Reconciliation + backfill | Archive-only или деcommission |
| **sync-subscriptions** (GHA cron) | Sync fp → grants | Основной (пока webhook не покрывает все каналы) | Reconciliation-only |
| **Aisystant PG** | Source of truth ch1–5 | Параллельный источник (dual-read) | Legacy read-only |

</details>

---

<details>
<summary><b>§5. Потоки данных</b></summary>

## 5.1. Целевой поток (после миграции)

```
Пользователь → Провайдер (YooKassa/Stripe/Paybox)
                    │
                    ▼ webhook (push)
            Payment Receiver (CF Worker)
                    │
         ┌──────────┼──────────┐
         │          │          │
    verify     normalize   idempotent
    (IP/sig)   (→ unified)  (INSERT ON CONFLICT)
                    │
                    ▼
         finance_payments (Neon)
                    │
              ┌─────┴─────┐
              │            │
    sync-subscriptions   Metabase
    (cron / trigger)    (real-time)
              │
              ▼
    subscription_grants (Neon)
              │
        ┌─────┴─────┐
        │            │
    Gateway MCP    Бот
    (доступ)    (UI подписки)
```

## 5.2. Переходный поток (Стадия 1)

```
YooKassa/Stripe → Payment Receiver → finance_payments (Neon)
                       │
                       ▼
                 forward → Aisystant (Дима продолжает работать)
                                          ▲
Aisystant PG ──── incremental-sync ───────┘ (reconciliation-only)
```

Payment Receiver = основной поток. Forward обеспечивает совместимость:
- Дима продолжает получать webhook данные (через наш forward)
- incremental-sync переходит в режим reconciliation (сверка, не основной поток)
- Сверка ловит расхождения между forward и прямой записью

## 5.3. Поток identity enrichment (без изменений)

```
Оплата (любой канал) → finance_payments (email/telegram_id)
                              │
sync-subscriptions ───────────┘
                              │
                              ▼
                    subscription_grants (email/telegram_id, ory_id=NULL)
                              │
Gateway OAuth ────────────────┘
(Вариант A: UPDATE ory_id по email)
```

</details>

---

<details>
<summary><b>§6. Этапы перехода от монолита (3 стадии)</b></summary>

> **Принцип:** Strangler Fig — последовательная замена, не параллельный запуск.
> Три стадии отражают инверсию потока данных: pull → push+forward → push-only (Neon SSOT).

## Стадия 0: Текущее состояние

```
Провайдер → Дима (Aisystant) → мы тянем pull (incremental-sync)

YooKassa/Stripe/Тинькофф → Aisystant PG
                                  │
                     incremental-sync (GHA cron */10)
                                  │
                                  ▼
                        finance_payments (Neon)
```

- ch1–5: webhook приходит Диме → мы pull из Aisystant PG ✅
- ch6: бот → Aisystant webhook → мы pull ✅
- ch7: бот → Neon напрямую ✅ (WP-231 Ф-H)
- ch8: Directus → Neon напрямую ✅
- subscription_grants: sync каждые 30 мин ✅
- Gateway: читает subscription_grants ✅

**Проблемы:** задержка 10–40 мин, зависимость от Aisystant, нет real-time.

## Стадия 1: Мы принимаем webhook, пересылаем Диме

```
Провайдер → Payment Receiver (наш) → Дима (forward) + Neon (write)

YooKassa/Stripe → Payment Receiver (CF Worker)
                       │                │
                       ▼                ▼
              forward → Aisystant    finance_payments (Neon)
              (Дима продолжает       (мы пишем real-time)
               работать как раньше)
```

**Суть:** webhook URL переключается на нас. Мы:
1. Верифицируем подпись/IP
2. Нормализуем → записываем в `finance_payments` (Neon)
3. Пересылаем оригинальный webhook Диме → его системы продолжают работать без изменений

**Почему forward:** Дима не готов сразу перейти на чтение из Neon. Его CRM, биллинг-логика, подписки — всё ещё завязано на Aisystant PG. Forward позволяет не ломать его процессы.

**Порядок подключения каналов:**

| Волна | Каналы | Почему в таком порядке |
|-------|--------|----------------------|
| 1.1 | ch6 (ЮКасса-бот) | Бот контролирует webhook URL. Самый простой — один провайдер, один канал |
| 1.2 | ch3 (Stripe) | Отдельный аккаунт Corp (USA), HMAC verification. Важен для мирового рынка (WP-215) |
| 1.3 | ch1,2,4,5 (Aisystant каналы) | Координация с Димой: он переключает webhook URL на нас |

**Артефакты:**
- `DS-MCP/payment-receiver/` — Cloudflare Worker
- `processed_webhooks` таблица в Neon (idempotency)
- Forward-прокси: HTTP POST → Aisystant webhook endpoint
- Миграция в `DS-IT-systems/payment-registry/`

**Критерии перехода на Стадию 1:**
- [ ] Payment Receiver деплоен и принимает webhook
- [ ] Хотя бы один канал переключён (ch6 — первый)
- [ ] Forward работает — Дима получает те же данные
- [ ] finance_payments в Neon обновляется real-time
- [ ] incremental-sync переходит в режим reconciliation (сверка, не основной поток)

**Критерий успеха волны 1.1:** оплата через бота ЮКасса → webhook → Payment Receiver → finance_payments (Neon) + forward → Aisystant. E2E < 5 секунд.

## Стадия 2: Мы принимаем webhook, Дима читает из Neon

```
Провайдер → Payment Receiver → Neon (SSOT)
                                  │
                    ┌─────────────┼──────────────┐
                    ▼             ▼               ▼
              Дима (CRM)    Gateway MCP      Metabase
              (читает       (subscription    (аналитика)
               из Neon)      _grants)
```

**Суть:** Forward отключается. Дима переключает свои сервисы на чтение из Neon. Neon = единый реестр платежей (SSOT). Это целевая архитектура WP-228.

**Что меняется:**
- Forward-прокси → отключается
- incremental-sync → отключается полностью (или archive-only)
- Дима: CRM читает `finance_payments` из Neon (API/view)
- Биллинг-логика (подписки, стажировки) → поэтапно мигрирует или остаётся в Aisystant, но данные берёт из Neon

**Предпосылки (не блокируют Стадию 1):**
- WP-228 DP.ARCH.004: целевая архитектура Neon определена
- Дима готов переключить CRM на Neon
- API/view для чтения finance_payments из Neon

**Критерии завершения (целевое состояние):**
- [ ] Все 8 каналов записывают в finance_payments (Neon) напрямую
- [ ] Подписки из всех каналов фиксируются в subscription_grants
- [ ] Дима (CRM) читает из Neon, не из Aisystant PG
- [ ] Forward отключён
- [ ] incremental-sync отключён или в archive-only режиме
- [ ] Gateway корректно проверяет подписки из всех каналов

## Сравнение стадий

| Аспект | Стадия 0 (сейчас) | Стадия 1 (переход) | Стадия 2 (целевая) |
|--------|-------------------|--------------------|--------------------|
| Кто получает webhook | Дима | Мы | Мы |
| Кто пишет в Neon | incremental-sync (pull) | Payment Receiver (push) | Payment Receiver (push) |
| Дима получает данные | Напрямую от провайдера | Forward от нас | Читает из Neon |
| Задержка в Neon | 10–40 мин | < 5 сек | < 5 сек |
| incremental-sync | Основной поток | Reconciliation | Отключён |
| Единый реестр (SSOT) | Aisystant PG | Два параллельных | Neon |

</details>

---

<details>
<summary><b>§7. Безопасность (Security Gate)</b></summary>

## PII Gate (CLAUDE.md B7.3)

Payment Receiver обрабатывает PII: email, telegram_id, платёжные данные.

| Мера | Реализация |
|------|-----------|
| **Верификация webhook** | IP whitelist (YooKassa) + HMAC signature (Stripe) |
| **HTTPS only** | CF Worker — HTTPS по умолчанию |
| **No PII in logs** | Логировать event_id, channel, amount. НЕ логировать email, telegram_id |
| **raw_payload encryption** | raw_payload (полный webhook) → encrypt at rest (Neon TDE или отдельная колонка) |
| **Rate limiting** | CF WAF rate limiting на `/webhook/*` |
| **Audit trail** | processed_webhooks + finance_payments + audit.log |
| **Доступ к Neon** | Dedicated role `payment_receiver_writer` (минимальные привилегии) |

## Threat Model

| Угроза | Защита |
|--------|--------|
| Replay attack | Idempotency (processed_webhooks) + timestamp validation |
| Spoofed webhook | IP whitelist (YooKassa) + signature (Stripe) |
| Data exfiltration | CF Worker не хранит state, Neon encrypted at rest |
| DDoS | CF edge protection, rate limiting |
| SQL injection | Parameterized queries через neon() driver |

</details>

---

<details>
<summary><b>§8. Сопоставление с существующими РП</b></summary>

| РП | Как связан с WP-246 | Влияние | Стадия |
|----|---------------------|---------|--------|
| **WP-73** (Архитектура) | Решение встречи 13 апр: Neon единый реестр. WP-246 реализует это для платежей. **Добавить в повестку:** 3-стадийная модель перехода, координация с Димой (Стадия 1 forward, Стадия 2 чтение из Neon) | Обсудить на встрече | 1→2 |
| **WP-228** (Neon Data Map) | Добавляется `processed_webhooks` таблица + `payment_receiver_writer` роль. **Стадия 2** = целевая архитектура DP.ARCH.004 (Дима читает из Neon) | Обновить DP.ARCH.004 | 1+2 |
| **WP-183** (CRM/Payments) | finance_payments = целевая таблица. **Стадия 1:** incremental-sync → reconciliation-only (сверка). **Стадия 2:** sync отключается полностью | Sync меняет роль → отключается | 1→2 |
| **WP-231** (Подписки) | subscription_grants наполняется быстрее (real-time vs 30 мин). Stars-подписки (Ф-H DONE) — прецедент | Ускорение, не изменение | 1 |
| **WP-215** (РФ/Мир) | ch3 (Stripe, Corp) = мировой рынок, ch1,2,4,5,6,7 = РФ | region column уже в плане WP-231 Ф-C | 1 |
| **WP-212** (Безопасность) | PII в webhook, новый endpoint `/webhook/*`. Security Gate пройден в Ф0 | Обновить чеклист безопасности | 1 |
| **WP-210** (Gateway auth) | Gateway читает subscription_grants — без изменений | Ускорение доступа | — |
| **WP-109** (Activity Hub) | Может подписаться на события Payment Receiver | Future: event bus | 2+ |

</details>

---

<details>
<summary><b>§9. Открытые вопросы</b></summary>

| # | Вопрос | Кто решает | Блокирует | Стадия |
|---|--------|-----------|-----------|--------|
| Q1 | YooKassa поддерживает multiple webhook URLs для одного магазина? Если нет — переключение = мы принимаем, forward Диме | Проверить API/документацию | Волну 1.3 (ch1,2,4,5) | 1 |
| Q2 | Webhook URL Stripe: кто настраивает (мы или Дима)? | Дима/Ильшат | Волну 1.2 (ch3) | 1 |
| Q3 | `charged_off_at` из webhook: как определить? | Дима (семантика chargeoff в Aisystant) | Нормализацию | 1 |
| Q4 | `purpose` из webhook: как маппить? (YooKassa metadata vs description) | Анализ кода бота | Нормализацию | 1 |
| Q5 | Биллинг-логика (подписки, стажировки) остаётся в Aisystant? | Решение М3 (WP-183) — да | Scope Стадии 2 | 2 |
| Q6 | Готов ли Дима переключить webhook URL ch1-5 на нас? Endpoint для forward? | Дима | Волну 1.3 | 1 |
| Q7 | `valid_until` для разных типов подписок? | Дима/Ильшат | sync-subscriptions | 1 |
| Q8 | Готов ли Дима переключить CRM на чтение из Neon? Какие API/view нужны? | Дима | Стадию 2 целиком (Ф7) | 2 |

</details>

---

<details>
<summary><b>§10. Обновление фаз WP-246</b></summary>

По итогам исследования фазы уточнены и привязаны к 3 стадиям перехода (§6):

### Стадия 1: Мы принимаем webhook, пересылаем Диме

| Фаза | Что | Бюджет | Зависимости |
|------|-----|--------|-------------|
| **Ф0** | Исследование + концепция + IntegrationGate + ArchGate (этот документ) | 5h | — | **DONE** |
| **Ф1** | Payment Receiver MVP: scaffold CF Worker, YooKassa handler, processed_webhooks, forward-прокси | 4h | Ф0 |
| **Ф1.1** | Stars-подписки в боте (UI «Оплатить звёздами») | 3h | — (независимо) |
| **Ф2** | ch6 ЮКасса-бот → Payment Receiver (волна 1.1) | 3h | Ф1 |
| **Ф3** | Stripe handler ch3 + HMAC verification (волна 1.2) | 3h | Ф1, Q2 |
| **Ф4** | Reconciliation: incremental-sync → сверка-only | 2h | Ф2 или Ф3 |
| **Ф5** | ch1,2,4,5 — координация с Димой: переключить webhook URL на нас, forward ему (волна 1.3) | 4h | Q1, Q6, Дима |
| **Ф6** | subscription_grants для всех каналов (trigger или cron < 1 мин) | 2h | Ф5 |

### Стадия 2: Дима читает из Neon (целевая)

| Фаза | Что | Бюджет | Зависимости |
|------|-----|--------|-------------|
| **Ф7** | API/view для CRM Aisystant: Дима переключает чтение на Neon | 3h | Ф5, Ф6, координация с Димой, WP-228 |
| **Ф8** | Отключение forward-прокси + incremental-sync → archive-only | 1h | Ф7 |
| **Ф9** | E2E верификация: все каналы → Neon → Дима читает → Gateway проверяет | 3h | Ф7, Ф8 |

**Общий бюджет:** ~33h (из них 5h Ф0 потрачены)

**Примечание:** Стадия 2 зависит от готовности Димы переключить CRM на чтение из Neon. Между Стадией 1 и 2 может быть значительный временной разрыв. Forward-прокси обеспечивает стабильную работу в переходный период

</details>

---

*Документ создан: 2026-04-16. Автор: Церен Церенов.*
*Основан на исследовании SOTA: Payment Orchestration, Webhook-First Architecture, Strangler Fig Pattern.*
*Связанные артефакты: DP.SC.112, DP.ARCH.004, WP-183 context, WP-231 context.*
