---
family: F5
kernel: C
system: C2
role: Architecture
status: draft
created: 2026-04-09
depends_on: [WP-121, WP-109]
source: "WP-121 context, DP.SC.105, DP.ARCH.003"
---

# Доменная модель системы баллов

> **Source-of-truth (обещание):** SC.105 — Экономика вклада.
> **Source-of-truth (ЦД):** DP.ARCH.003 — 3-слойная архитектура ЦД.
> Здесь — реализационная модель: таблицы, потоки, инварианты.

---

## 1. Ключевое различение

**Баллы = вычисляемая проекция**, а не хардкод. Один поток неизменяемых событий (user_events) + набор правил (point_rules) = начисления (point_transactions). Пересчёт = replay всех events по текущим rules.

```
user_events (факты, append-only)
  │
  ▼
Readiness Gate (WP-109 Ф4)
  │ все источники synced + checksum ok?
  ▼
calculate_points()
  │ event + point_rules → point_transaction
  ▼
finance.point_transactions (начисления, append-only)
  │
  ▼
finance.point_balances (агрегат, пересчитываемый)
  │
  ▼
Бот: /points (пользователь видит)
```

---

## 2. Сущности

### 2.1. point_rules — правила начисления

Определяют: какой event_type → сколько баллов.

```sql
CREATE TABLE finance.point_rules (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,         -- 'topic_created', 'test_passed', ...
    source TEXT,                      -- 'lms', 'bot', NULL=любой
    points INTEGER NOT NULL,          -- базовые баллы
    multiplier_field TEXT,            -- 'qualification_level' → множитель
    max_per_day INTEGER,              -- anti-abuse: лимит в день
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Правила **версионируются**: новые правила добавляются (active=true), старые деактивируются (active=false). Replay за прошлый период — по правилам, действовавшим в тот момент (TODO: `valid_from` / `valid_until`).

### 2.2. point_transactions — журнал начислений

Append-only. Один event = максимум одна транзакция (UNIQUE event_id).

```sql
CREATE TABLE finance.point_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_uuid UUID NOT NULL,          -- ory_id
    event_id BIGINT NOT NULL UNIQUE,  -- → user_events.id (1:1)
    rule_id INTEGER NOT NULL,         -- → point_rules.id
    points INTEGER NOT NULL,          -- начисленные баллы (отрицательные для correction/spent)
    type TEXT DEFAULT 'earned',       -- 'earned', 'correction', 'expired', 'spent'
    source_region TEXT,               -- 'ru', 'world' — для аудита и будущего разделения
    reference_id BIGINT,             -- для correction → original transaction id
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Типы транзакций:
- **earned** — начисление по правилу (calculate_points)
- **spent** — списание при оплате баллами (Billing Service, WP-183)
- **correction** — ручная корректировка (±, с reference на оригинал)
- **expired** — истечение срока (если будет политика expiry)

### 2.3. point_balances — агрегированный баланс

```sql
CREATE TABLE finance.point_balances (
    user_uuid UUID PRIMARY KEY,
    total_earned INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    total_corrections INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,        -- earned - spent + corrections
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Пересчитываемый:** `balance = SUM(points) FROM point_transactions WHERE user_uuid = X`. Таблица — кэш для быстрого чтения. При replay — полный пересчёт.

---

## 3. Инварианты

| # | Инвариант | Механизм |
|---|-----------|----------|
| 1 | Один event = максимум одно начисление | UNIQUE(event_id) в point_transactions |
| 2 | Events неизменяемы | Append-only, нет UPDATE/DELETE |
| 3 | Транзакции неизменяемы | Append-only. Ошибка → correction (новая запись) |
| 4 | Баланс = сумма транзакций | point_balances = materialized SUM |
| 5 | Начисление только при Readiness Gate OK | calculate_points() проверяет sync_log |
| 6 | Idempotent replay | Тот же event + тот же rule = тот же результат |

---

## 4. Потоки данных

### 4.1. Начисление (earned)

```
user_events.INSERT (через Activity Hub)
  → pg_notify('new_event', event_id)  [WP-109 Ф5, Event Bus]
  → Dispatcher → points_service
  → Readiness Gate: все источники synced?
  → calculate_points(event, rules) → point_transaction
  → UPDATE point_balances
```

### 4.2. Списание (spent)

```
Участник → /buy_with_points → Billing Service (WP-183)
  → SELECT balance FROM point_balances WHERE user_uuid = X
  → balance >= price?
  → INSERT point_transactions (type='spent', points=-N)
  → UPDATE point_balances
  → Выдать доступ
```

### 4.3. Replay (пересчёт)

```
Триггер: новые правила / исправление ошибки / аудит
  → TRUNCATE point_transactions (или archive)
  → FOR EACH event IN user_events ORDER BY created_at:
      calculate_points(event, rules_at(event.created_at))
  → Пересчёт point_balances
```

---

## 5. Readiness Gate (WP-109 Ф4)

Перед каждым вызовом `calculate_points()`:

1. Каждый source: последний sync = success, не старше 48h
2. Checksum: count в API источника == count в Neon (расхождение ≤3%)
3. Все проверки пройдены → начисление. Хоть одна не пройдена → СТОП + алерт

Без Readiness Gate баллы начислялись бы по неполным данным → неточные балансы → потеря доверия.

---

## 6. Связь с ЦД (DP.ARCH.003)

Система баллов — **ещё одна проекция** в архитектуре ЦД:

| Слой ЦД | Что |
|---------|-----|
| Events | user_events (общий поток) |
| State | point_balances, streak, qualification (проекции) |
| Views | /points в боте, дашборд в Metabase |

Квалификация (стадия развития: Random → Proactive) вычисляется ЦД и **читается** Points Engine для множителя. Points Engine **не вычисляет** квалификацию сам.

---

*Создано: 2026-04-09. WP: 121.*
