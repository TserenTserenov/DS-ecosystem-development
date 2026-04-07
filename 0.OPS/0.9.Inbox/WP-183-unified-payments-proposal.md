# WP-183: Единый учёт оплат и автоматизация допуска

> **Статус:** согласование после встречи 5 (7 апр 2026)
> **Участники:** Дима (Aisystant), Ильшат (менеджмент), Гиляна (бухгалтерия), Алёна (маркетинг), Юля (декан), Церен и Андрей (архитектура)

---

## 1. Принятые решения (коротко)

**Neon = единый Реестр оплат.** Все 8 каналов оплаты → Neon. Все потребители (Directus, Metabase, бот Aist, Aisystant) читают из Neon.

**Переходный период (dual-write):** Aisystant продолжает писать в свою PG + дублирует каждый платёж/списание в Neon. Каналы 6-8 пишут в Neon напрямую. Aisystant читает из Neon для проверки оплат (баны, подписки). Данные из Aisystant НЕ удаляются до полного перехода.

**Биллинг-логика пока остаётся в Aisystant** — заберём позже. В Aisystant 2 таблицы (`payment` + `charge_off`), в Neon — **1 таблица** `finance.payments` (объединены). Успешные списания = записи с `charged_off_at IS NOT NULL`.

**Монета** — вручную через Directus → Neon. Автоинтеграция — позже.

**Индивидуальные ссылки YooKassa** — API уже есть на бэке Aisystant для 3 платёжных систем.

> Подробнее о всех решениях (Р1-Р6, А1-А4, Д1-Д4, М1-М8) и переходном периоде — [§6. Подробно о принятых решениях](#6-подробно-о-принятых-решениях).

---

## 2. Что нужно согласовать

**2.1.** Этапы реализации Фазы A → [§3](#3-этапы-реализации)

**2.2.** Дима: схема `finance.payments` в Neon (1 таблица, 2 таблицы Aisystant объединены) → [§4](#4-схема-finance-в-neon)
- Все ли поля на месте для dual-write?
- Маппинг 2 → 1 понятен? (payment → INSERT, charge_off → INSERT с `charged_off_at`)
- Маппинги `purpose`, `status`, `channel` — корректны?

**2.3.** Ильшат: как бот МИМ (@SystemsSchool_bot) передаёт данные в Neon? Webhook или напрямую?

**2.4.** Открытые вопросы для Гиляны/Алёны/Юли → [§5](#5-открытые-вопросы)

---

## 3. Этапы реализации

### Фаза A: Единый учёт + dual-write (можно без Ory)

```
Каналы 1-5 (YooKassa, Paybox, Stripe, Монета, Tilda):
  Webhook → Aisystant PG (как сейчас) → dual-write → Neon

Каналы 6-7 (YooKassa семинары, TG Stars):
  Webhook → Бот Aist → Neon (как сейчас)

Канал 8 (Manual, B2B):
  Directus → Neon

Aisystant (чтение): проверяет платежи в своей PG + в Neon
```

| # | Что | Кто | Dep | Срок | Результат |
|---|-----|-----|-----|------|-----------|
| 1 | **Схема `finance.payments` в Neon** — 1 таблица (§4) | Церен | -- | W15 | Готовая схема. Дима валидирует |
| 2 | **Экспорт истории** из Aisystant PG → Neon | Церен + Дима | 1 + доступ (Паша) | W15-16 | Исторические данные каналов 1-5 в Neon |
| 3 | **Dual-write: Aisystant → Neon** после save(). Деплой вечером | Дима | 1 | W15-16 | Каждый новый платёж/списание дублируется |
| 4 | **Read: Aisystant читает из Neon** (баны, подписки) | Дима | 1 | W16 | Aisystant видит оплаты каналов 6-8 |
| 5 | **Directus на Railway** + ручной ввод (Монета, B2B) | Церен | 1 | W15 | Единое окно для руководства |
| 6 | **Metabase на Railway** + дашборды | Церен | 5 | W16 | Выручка, воронка, наполняемость |
| 7 | **Сверка** 24ч: cron сравнивает Aisystant PG и Neon | Церен | 3 | W16 | Гарантия целостности dual-write |
| 8 | **Автодопуск + маршрутка** (бот Aist ↔ Neon) | Церен | 3 | W16-17 | Автоматический допуск по всем 8 каналам |
| 9 | **Инд. ссылки на оплату с сайта** (YooKassa) | Церен + сайт | 3 | W17 | Замена общих ссылок на индивидуальные |

**Бюджет Фазы A:** ~22h. **Критический путь:** 1 → 2 → 3. **Параллельно:** 5, 6.

**Что работает после Фазы A:**
- Neon = единый Реестр оплат (все 8 каналов)
- Aisystant работает как сейчас + дублирует в Neon + читает из Neon
- Бот Aist видит все оплаты, автодопуск и маршрутка по всем каналам
- Directus + Metabase — единое окно для руководства
- Сверка 24ч: алерт при расхождении

### Фаза B: Единый аккаунт через Ory (после WP-187)

| # | Что | Кто | Dep | Бюджет |
|---|-----|-----|-----|--------|
| B1 | Управление доступами через Ory | Tseren + Дима | WP-187 | 4h |
| B2 | Миграция аккаунтов (telegram + email + aisystant → один) | Tseren + Дима | B1 | 2h |
| B3 | Бот Aist проверяет доступы через Ory | Tseren | B1 | 3h |
| B4 | Единый вход в Directus через Ory | Tseren | B1 | 1h |
| B5 | **Выход из переходного периода.** Dual-write отключен, Neon = единственный источник | Дима + Tseren | B1-B3, 0 расхождений 2 нед | 4h |

**Бюджет Фазы B:** ~14h.

### Фаза C: Экономика (после A+B)

| # | Что | Dep | Бюджет |
|---|-----|-----|--------|
| C1 | Баллы (Points Engine, WP-121) | Фаза B | 6h |
| C2 | Revenue Sharing (30/50/15/5%) | Фаза A | 3h |
| C3 | Юнит-экономика в Metabase | Фаза A | 2h |

**Бюджет Фазы C:** ~11h.

---

## 4. Схема `finance.*` в Neon

> На основе анализа Java-сущностей Aisystant: `Payment` (18 колонок), `ChargeOff` (10 колонок), `PaymentPurpose`, `PaymentUtil`, `AccessService`.

### Почему 1 таблица, а не 2 как в Aisystant

В Aisystant — 2 таблицы: `payment` (все попытки оплат) и `charge_off` (успешные списания). Исторически они разделены для поддержки баланса пользователя (payments минус charge_offs).

В Neon объединяем в **1 таблицу `finance.payments`**, потому что:
- `charge_off` — это не отдельная сущность, а **факт успешного списания** по платежу
- Биллинг-логику пока не переносим (М3) — нам не нужна раздельная модель баланса
- Проще запросы: «все операции по пользователю» = один SELECT
- Когда заберём биллинг — схема уже готова

Различие payment / charge_off сохраняется через поле `charged_off_at`:
- `NULL` = платёж без списания (неуспешный, в процессе или ещё не обработан)
- `NOT NULL` = списание выполнено (успешная оплата, деньги зачислены)

### Как Дима маппит 2 таблицы → 1

**При `paymentRepository.save(payment)`:**
```
INSERT INTO finance.payments (
    source_id, source_table, suser_id,
    purpose, code, amount, currency,
    payment_system, channel, source_system,
    status, success, processed,
    payment_index, autopay, autopay_data, auto_extend,
    locale, error_data, ext_id, timestamp
) VALUES (
    payment.id, 'payment', payment.suser_id,
    -- purpose: ordinal → string (см. маппинг ниже)
    'SUBSCRIPTION', payment.code, payment.amount, payment.currency,
    payment.payment_system, <channel по payment_system>, 'aisystant',
    payment.status, payment.success, payment.processed,
    payment.payment_index, payment.autopay, payment.autopay_data, payment.auto_extend,
    payment.locale, payment.error_data, payment.ext_id, payment.timestamp
);
-- charged_off_at = NULL (это попытка оплаты, не списание)
```

**При `chargeOffRepository.save(chargeOff)`:**
```
INSERT INTO finance.payments (
    source_id, source_table, suser_id,
    purpose, code, amount, currency,
    channel, source_system,
    payment_index, details, potok_id, timestamp,
    success, charged_off_at
) VALUES (
    chargeOff.id, 'charge_off', chargeOff.suser_id,
    'SUBSCRIPTION', chargeOff.code, chargeOff.amount, chargeOff.currency,
    <channel>, 'aisystant',
    chargeOff.payment_index, chargeOff.details, chargeOff.potokId, chargeOff.timestamp,
    true, NOW()  -- charge_off = всегда успешное списание
);
```

**Как читать:**
- Все платежи: `SELECT * FROM finance.payments WHERE source_table = 'payment'`
- Только успешные списания (аналог charge_off): `SELECT * FROM finance.payments WHERE charged_off_at IS NOT NULL`
- Есть ли оплата за семинар: `SELECT 1 FROM finance.payments WHERE charged_off_at IS NOT NULL AND purpose = 'WORKSHOP' AND code = 'SE-2026.2-T' AND suser_id = 123`

### Принципы схемы

- Все поля Aisystant отражены (для корректного dual-write)
- `double → decimal` (округление до 1 руб.)
- `purpose` как string enum (не ordinal int)
- Новые поля: `channel` (1-8), `source_system`, `source_table`, `charged_off_at`, `notified_bot`
- Мягкое удаление: `archived_at` (Д3)

### 4.1. finance.payments

Единая таблица: все платежи + списания. Источник: Aisystant (каналы 1-5) + бот Aist (6-7) + Directus (8).

```sql
CREATE SCHEMA IF NOT EXISTS finance;

CREATE TABLE finance.payments (
    id              BIGSERIAL PRIMARY KEY,
    ext_id          TEXT,                    -- внешний ID от платёжной системы
    source_id       BIGINT,                  -- оригинальный id из Aisystant (для сверки)
    source_table    TEXT NOT NULL DEFAULT 'payment', -- 'payment' или 'charge_off' (откуда пришла запись)

    -- Кто
    suser_id        BIGINT,                  -- Aisystant user ID (переходный период)
    telegram_id     BIGINT,                  -- Telegram user ID
    email           TEXT,
    ory_id          UUID,                    -- Фаза B

    -- Что
    purpose         TEXT NOT NULL CHECK (purpose IN ('BALANCE','SUBSCRIPTION','DONATION','INTERNSHIP','WORKSHOP')),
    code            TEXT,                    -- код тарифа/курса/потока/семинара
    amount          NUMERIC(12,2) NOT NULL,
    currency        TEXT NOT NULL DEFAULT 'RUB',

    -- Откуда
    payment_system  TEXT,                    -- 'yoo', 'paybox', 'stripe', 'tg_stars'
    channel         SMALLINT NOT NULL,       -- 1-8
    source_system   TEXT NOT NULL DEFAULT 'aisystant',

    -- Статус
    status          TEXT,                    -- 'succeeded', 'canceled', 'pending', 'ok', 'paid', etc.
    success         BOOLEAN NOT NULL DEFAULT false,
    processed       BOOLEAN NOT NULL DEFAULT false,
    charged_off_at  TIMESTAMPTZ,             -- NULL = платёж, NOT NULL = успешное списание

    -- Подписка
    payment_index   INTEGER,
    autopay         BOOLEAN NOT NULL DEFAULT false,
    autopay_data    TEXT,
    auto_extend     BOOLEAN,
    locale          TEXT,
    error_data      TEXT,

    -- Контекст списания (из charge_off)
    details         TEXT,                    -- детали списания
    potok_id        BIGINT,                  -- ID потока (когорты)

    -- Бот
    notified_bot    BOOLEAN NOT NULL DEFAULT false,

    -- Метаданные
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    archived_at     TIMESTAMPTZ
);

CREATE INDEX idx_payments_suser ON finance.payments (suser_id) WHERE suser_id IS NOT NULL;
CREATE INDEX idx_payments_telegram ON finance.payments (telegram_id) WHERE telegram_id IS NOT NULL;
CREATE INDEX idx_payments_ext_id ON finance.payments (ext_id) WHERE ext_id IS NOT NULL;
CREATE INDEX idx_payments_ory ON finance.payments (ory_id) WHERE ory_id IS NOT NULL;
CREATE INDEX idx_payments_charged_off ON finance.payments (charged_off_at) WHERE charged_off_at IS NOT NULL;
CREATE INDEX idx_payments_not_notified ON finance.payments (created_at) WHERE notified_bot = false AND success = true;
CREATE INDEX idx_payments_channel_ts ON finance.payments (channel, timestamp);
CREATE INDEX idx_payments_source ON finance.payments (source_table, source_id);
```

### 4.4. Маппинги

**`purpose` ordinal → string:**

| Ordinal (Aisystant PG) | String (Neon) |
|---|---|
| 0 | BALANCE |
| 1 | SUBSCRIPTION |
| 2 | DONATION |
| 3 | INTERNSHIP |
| 4 | WORKSHOP |

**`channel`:**

| # | Канал | `source_system` |
|---|-------|-----------------|
| 1 | YooKassa (подписки, потоки) | aisystant |
| 2 | Paybox | aisystant |
| 3 | Stripe | aisystant |
| 4 | Монета/PayAnyWay | aisystant |
| 5 | Tilda + Ecwid | aisystant |
| 6 | YooKassa (семинары бота) | bot_aist |
| 7 | TG Stars | bot_aist |
| 8 | Manual (B2B) | directus |

**`status` → `success`:**

| `payment_system` | `success = true` | `success = false` | Промежуточный |
|---|---|---|---|
| yoo | `succeeded` | `canceled` | `pending` |
| paybox | `ok` | `failed`, `incomplete`, `revoked`, `refunded`, `pb_result_error` | `pb_created` |
| stripe | `paid` | `expired` | (session status) |

---

## 5. Открытые вопросы

**Для Ильшата:**
- Бот МИМ (@SystemsSchool_bot) — как передаёт данные в Neon?
- Интеграция с Монетой (автоматическая) — следующий шаг

**Для Гиляны:**
- Какие отчёты нужны? (выручка, средний доход, выгрузка)
- Нужна ли сверка между каналами?
- Как учитываются оплаты через Aisystant Corp (Stripe, USD)?

**Для Алёны:**
- Какие разрезы для маркетинга? (каналы, когорты, продукты, география)
- Нужна ли воронка (лид → оплата → в чате → активный)?

**Для Юли:**
- Наполняемость групп — какая информация нужна?
- Преподаватели — нужен ли доступ через Directus?

**Для Димы:**
- `telegram_id` при оплате через Tilda/Ecwid — решение через Ory (Фаза B)

**Архитектура (Церен + Андрей):**
- Баллы (WP-121): нужна ли `finance.point_transactions` как placeholder?
- Revenue Sharing: считать в Metabase или в Billing Service?
- Activity Hub (WP-109): Billing adapter — когда?
- Permissions: карта функция → permission

---

## 6. Подробно о принятых решениях

<details>
<summary><b>6.1. Архитектурные решения (5 встреч, 26 мар -- 7 апр)</b></summary>

### Основные (Р1-Р6)

| # | Решение | Обоснование |
|---|---------|-------------|
| Р1 | **Payment Registry (SYS.011)** — подсистема платформы. Реестр оплат = таблицы в Neon. В переходный период: Aisystant дублирует каналы 1-5 в Neon; каналы 6-8 пишут напрямую | Один источник (Neon), не два |
| Р2 | **Две системы:** Payment Registry (учёт) и Billing Service (SYS.010, бизнес-логика). На Фазе B Payment Registry мигрирует в Billing Service | Разделение факта оплаты и бизнес-логики |
| Р3 | **Уведомление бота через Neon** (PG NOTIFY / Directus Flow / polling). Бот НЕ получает webhook от Aisystant напрямую | Один источник данных, бот читает оттуда |
| Р4 | **Привязка identity через Ory (Фаза B).** Звезда, не mesh. Без костылей до Ory | O(n^2) интеграций при mesh |
| Р5 | **Допуск в чат:** (A) бот генерирует одноразовую ссылку, (B) админ через TG. Оба варианта отслеживаются | Вариант A предпочтительнее |
| Р6 | **Бот МИМ тоже принимает оплаты** → пишет в Neon | Не терять канал |

### Архитектор (29 мар): А1-А4

| # | Решение |
|---|---------|
| А1 | RLS подтверждён — Directus поверх RLS-политик |
| А2 | Access Management = ORY Keto (отдельно от Billing) |
| А3 | Chargeback — не нужен пока |
| А4 | CRM = Directus + Metabase — подтверждён |

### Встреча 4 с архитектором (7 апр): Д1-Д4

| # | Решение |
|---|---------|
| Д1 | Identity: `ory_id` = единственный ID. Каждый сервис — локальная учётка при первом входе |
| Д2 | ЦД↔LMS при первом входе (не массовая миграция) |
| Д3 | Мягкое удаление: `archived_at`, не физическое |
| Д4 | Безопасность: практики сертификаций (SOC 2, ISO 27001) |

### Встреча 5 с командой (7 апр): М1-М8

| # | Решение | Обоснование |
|---|---------|-------------|
| М1 | **Dual-write + read.** Каналы 1-5: Aisystant → свою PG + Neon. Каналы 6-8: Neon. Aisystant читает из Neon. Данные не удаляются | Дима: «на первом этапе проверять: есть ли платёж в текущей базе ИЛИ в Neon» |
| М2 | **Монета — вручную через Directus → Neon.** Церен разворачивает Directus | Дима: «Монеты здесь нет. Всё вручную» |
| М3 | **Биллинг пока остаётся в Aisystant.** Заберём позже | Дима: «Он работает, пока не трогаем» |
| М4 | **`charge_off` = основа для решений**, не `payment` | Дима: «charge_off только если платёж успешно проведён» |
| М5 | **Neon API для всех подсистем.** Церен делает | Дима: «Если доступ есть, проблем не вижу» |
| М6 | **Инд. ссылки YooKassa** — API уже есть для 3 систем | Дима: «API на бэке работает» |
| М7 | **Церен: схема → Дима: валидация** | Дима: «подключусь и проверю» |
| М8 | **Деплой вечером** | Дима: «лучше поздно, когда меньше народа» |

</details>

<details>
<summary><b>6.2. Переходный период: гибридная схема dual-write</b></summary>

> AS-IS → ПЕРЕХОДНЫЙ ПЕРИОД → TO-BE

**AS-IS (сейчас):**
```
Каналы 1-5 → Aisystant PG (единственное хранилище)
Каналы 6-7 → Neon (единственное хранилище)
Канал 8    → нигде (вручную)

Aisystant НЕ видит каналы 6-8.
Бот Aist НЕ видит каналы 1-5 (кроме API подписок с cache 5мин).
```

**ПЕРЕХОДНЫЙ ПЕРИОД (Фаза A):**
```
Каналы 1-5 → Aisystant PG (как сейчас) → dual-write → Neon
Каналы 6-7 → Neon (как сейчас)
Канал 8    → Directus → Neon

Aisystant PG:
  - ПИШЕТ: каналы 1-5 (без изменений)
  - ДУБЛИРУЕТ: save(payment) → INSERT в Neon, save(charge_off) → INSERT с charged_off_at
  - ЧИТАЕТ: свою PG + Neon (для банов, подписок)
  - НЕ получает данные из Neon (без обратного дублирования)

Neon = единый Реестр оплат (все 8 каналов)

Биллинг-логика Aisystant:
  - Работает на СВОИХ таблицах — без изменений
  - Дополнительно: проверяет Neon (каналы 6-8)
  - Решения на основе charged_off_at IS NOT NULL (М4)
```

**Инварианты:**
1. Aisystant ничего не теряет
2. Neon = надмножество (все 8 каналов)
3. Дублирование одностороннее: Aisystant → Neon
4. Сверка 24ч: алерт при расхождении

**Критерии выхода (→ TO-BE):**
1. 0 расхождений за 2 недели
2. Aisystant читает из Neon и принимает решения
3. Ory развёрнут (WP-187)
4. Биллинг переведён на Neon

**TO-BE:**
```
Все каналы → Neon (единственный источник)
Aisystant = потребитель (read-only)
```

</details>

---

## 7. Контекст и материалы

<details>
<summary><b>7.1. Проблема: два мира</b></summary>

```
МИР 1: Aisystant (Java LMS)              МИР 2: Бот Aist (Python)
|- YooKassa (подписки, потоки)            |- YooKassa (семинары витрины)
|- Paybox                                 |- TG Stars (семинары)
|- Stripe (Aisystant Corp)                +- Neon: seminar_payments
|- Монета/PayAnyWay
|- Tilda/Ecwid (витрина)
+- PostgreSQL Aisystant

         X НЕ СВЯЗАНЫ X
```

**Последствия:**
- Много ручной работы: оплата через Tilda/Ecwid → Алёна/Гиляна вручную invite → задержка, ошибки
- Гиляна не видит оплаты через бот Aist
- Маршрутка невозможна — бот не знает всех оплативших
- Нет единой выручки / среднего дохода

</details>

<details>
<summary><b>7.2. Карта каналов оплаты</b></summary>

### 8 каналов, 3 получателя

| # | Канал | Получатель | Обработка | Реестр (as-is) |
|---|-------|-----------|-----------|----------------|
| 1 | YooKassa (подписки, потоки) | ИП | Aisystant | PG Aisystant |
| 2 | Paybox | ИП | Aisystant | PG Aisystant |
| 3 | Stripe | Aisystant Corp | Aisystant | PG Aisystant |
| 4 | Монета/PayAnyWay | ИП | Aisystant | PG Aisystant |
| 5 | Tilda + Ecwid | ИП | Aisystant | PG Aisystant |
| 6 | YooKassa (семинары) | ИП | Бот Aist | Neon |
| 7 | TG Stars | Телеграм | Бот Aist | Neon |
| 8 | Manual (B2B) | ИП/Corp | Вручную | Нигде |

> **To-be (М1):** dual-write. Каналы 1-5 → Aisystant PG + Neon. Каналы 6-8 → Neon. Neon = единый Реестр оплат.

### Две системы учёта оплат

| Система | Что | Где сейчас | Куда идёт |
|---------|-----|-----------|-----------|
| **Payment Registry** (SYS.011) | Учёт транзакций. В Aisystant: 2 таблицы (`payment` + `charge_off`). В Neon: 1 таблица `finance.payments`. Успешные списания = `charged_off_at IS NOT NULL` (М4) | Внутри монолита Aisystant | Фаза A: dual-write в Neon |
| **Биллинг-логика** (модуль) | Подписки, стажировки, продление. **Пока остаётся**, заберём позже (М3) | Внутри монолита | Фаза B-C: мигрирует в Billing Service |
| **Billing Service** (SYS.010) | Новая: тарифы, подписки, баллы, revenue sharing | Не существует | Фаза B-C |

</details>

<details>
<summary><b>7.3. Архитектура (обновлено 7 апр)</b></summary>

```
                     Ory (аккаунты + доступы) [Фаза B]
                            |
                +-----------+-----------+
                v           v           v
         Aisystant      Neon PG        Бот Aist
         (монолит)    (Реестр оплат    (Python)
            |          = finance.*)        |
            |               |              |
            +-- dual-write -+   пишет -----+
                (каналы 1-5)    (каналы 6-8)
                                |
                    +-----------+-----------+
                    v                       v
              Directus                  Metabase
              (CRM UI,                (аналитика)
               ручной ввод)

              Activity Hub (WP-109)
                    +-> Billing adapter: платёж = событие
```

### Уведомление бота о новых оплатах (Neon → бот Aist)

| Механизм | Задержка | Сложность |
|----------|----------|-----------|
| **PG NOTIFY / LISTEN** | Реалтайм | Neon поддерживает |
| **Directus Flow** (trigger → webhook) | ~1 сек | Нет retry |
| **Polling** (каждые N сек) | До N сек | Простейший |

</details>

<details>
<summary><b>7.4. Сценарии оплаты</b></summary>

### Сценарий 1: Через бот Aist

```
Покупатель → бот Aist → ЮКасса → оплата
  → бот записывает в Neon → генерирует invite → покупатель в чате
```

### Сценарий 2: Через сайт МИМ

```
Покупатель → сайт → API Aisystant → инд. ссылка ЮКассы (М6) → оплата
  → Aisystant → PG + dual-write → Neon
  → бот узнаёт из Neon → генерирует invite → email + TG
```

### Сценарий 3: Семинары с сайта

```
AS-IS: Гиляна вручную
TO-BE: Aisystant → dual-write → Neon → бот → invite на email + TG
```

</details>

<details>
<summary><b>7.5. Lifecycle семинара</b></summary>

| Режим | Что |
|-------|-----|
| **Live** | Многоразовая ссылка. Кик неоплативших накануне |
| **Запись** | Только одноразовые ссылки. Многоразовая деактивирована |

| Допуск | Как |
|--------|-----|
| **A. Через бот** (предпочтительно) | Бот генерирует одноразовую ссылку |
| **B. Через админа** | Админ создаёт ссылку, бот видит вступление |

</details>

<details>
<summary><b>7.6. Воронка и доступы</b></summary>

### Воронка входа

```
T0 (анонимный) → T1 (зарегистрирован) → T2 (подписка БР)
  → T3 (ЦД подключён) → T4 (экзокортекс)
```

### Виды доступов

| Что | Сейчас | TO-BE |
|-----|--------|-------|
| Чат семинара (оплата через бот) | Бот шлёт invite | Без изменений |
| Чат семинара (оплата через сайт) | Гиляна/Алёна вручную | Dual-write → Neon → бот → invite |
| Подписка БР | API Aisystant (cache 5мин) | Ory (Фаза B) |
| Чат Сообщество IWE | Бот одобряет join | Ory → одобрить |
| B2B | Вручную | Directus → Neon → бот → invite |
| Маршрутка (кик) | Не реализовано | Cron: бот проверяет Neon → кик |

</details>

<details>
<summary><b>7.7. Связь с другими РП</b></summary>

| РП | Как связано |
|-----|------------|
| **WP-73** | §2.9 Биллинг — SYS.010 + SYS.011 |
| **WP-74** | SC-12 — витрина, deep links, маршрутка |
| **WP-109** | Activity Hub — Billing adapter |
| **WP-115** | E2E семинар: оплата → допуск → видео → маршрутка |
| **WP-121** | Points Engine — баллы как оплата |
| **WP-181** | Воронка чатов — бот читает Neon для авто-invite |
| **WP-187** | Ory — Фаза B зависит |
| **WP-188** | Маркетинг — Metabase дашборды |
| **WP-194** | Подписка БР — ценообразование |
| **WP-198** | Бот-вышибала — маршрутка: cron-кик |

</details>

---

*Создано: 2026-04-03. Обновлено: 2026-04-07 (встреча 5 — решения М1-М8, dual-write, реструктуризация документа).*
