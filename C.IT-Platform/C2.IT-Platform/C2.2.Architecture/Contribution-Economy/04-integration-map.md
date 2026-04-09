---
family: F5
kernel: C
system: C2
role: Architecture
status: draft
created: 2026-04-09
depends_on: [WP-121, WP-109, WP-183, WP-187]
---

# Карта интеграций системы баллов

> Кто пишет, кто читает, кто владеет. Все взаимодействия с Points Engine.

---

## 1. Владение таблицами

| Таблица | Владелец | Schema |
|---------|----------|--------|
| `finance.point_rules` | Points Engine (WP-121) | finance |
| `finance.point_transactions` | Points Engine (WP-121) | finance |
| `finance.point_balances` | Points Engine (WP-121) | finance |
| `development.user_events` | Activity Hub (WP-109) | development |
| `development.sync_log` | Activity Hub (WP-109) | development |

---

## 2. Матрица доступа

| Система | point_rules | point_transactions | point_balances | user_events |
|---------|-------------|-------------------|----------------|-------------|
| **Points Engine** | RW (владелец) | RW (владелец) | RW (владелец) | R |
| **Billing Service** (WP-183) | — | W (только type=spent) | R | — |
| **Activity Hub** (WP-109) | — | — | — | RW (владелец) |
| **Бот** | — | R (история) | R (баланс) | — |
| **Metabase** (WP-183) | R | R | R | R |
| **Readiness Gate** | — | — | — | R (+ sync_log) |

---

## 3. Потоки между системами

```
                    ┌─────────────┐
                    │  LMS        │
                    │  Бот        │──── ingest_event ────►┌──────────────┐
                    │  Клуб       │                       │ Activity Hub │
                    │  IWE (git)  │                       │ (WP-109)     │
                    │  CRM        │                       │              │
                    └─────────────┘                       │ user_events  │
                                                          └──────┬───────┘
                                                                 │
                                                          pg_notify (Ф5)
                                                                 │
                                                                 ▼
                                                          ┌──────────────┐
                    ┌─────────────┐    Readiness Gate      │ Points       │
                    │ sync_log    │◄──── проверка ─────────│ Engine       │
                    └─────────────┘                        │ (WP-121)     │
                                                           │              │
                                                           │ point_rules  │
                                                           │ point_txns   │
                                                           │ point_balance│
                                                           └──────┬───────┘
                                                                  │
                                              ┌───────────────────┼───────────────┐
                                              │                   │               │
                                              ▼                   ▼               ▼
                                       ┌────────────┐    ┌──────────────┐  ┌───────────┐
                                       │ Бот        │    │ Billing Svc  │  │ Metabase  │
                                       │ /points    │    │ (WP-183)     │  │ дашборды  │
                                       │ (R: баланс)│    │ (W: spent)   │  │ (R: всё)  │
                                       └────────────┘    └──────────────┘  └───────────┘
```

---

## 4. Интеграция с каждой системой

### 4.1. Activity Hub (WP-109) → Points Engine

| Аспект | Описание |
|--------|----------|
| Направление | Activity Hub → Points Engine (поток событий) |
| Механизм | pg_notify на INSERT в user_events (WP-109 Ф5, Event Bus) |
| Данные | event_id, event_type, user_uuid, source, payload, created_at |
| Частота | Реальное время (pg_notify) или batch (до появления Event Bus) |
| Fallback | Polling user_events WHERE NOT EXISTS in point_transactions |

### 4.2. Billing Service (WP-183) → Points Engine

| Аспект | Описание |
|--------|----------|
| Направление | Billing → Points Engine (списание) |
| Механизм | Прямой INSERT в point_transactions (type='spent') |
| Данные | user_uuid, points (отрицательное), type='spent', reference (invoice_id) |
| Проверка | SELECT balance FROM point_balances >= required_points |
| Транзакция | BEGIN → check balance → INSERT → UPDATE balances → COMMIT |
| Контуры | CRM-RU и CRM-EU оба могут списывать. source_region = 'ru'/'world' |

### 4.3. Бот → Points Engine

| Аспект | Описание |
|--------|----------|
| Направление | Бот ← Points Engine (чтение) |
| Команды | `/points` — баланс + последние начисления |
| Данные | point_balances.balance + последние 10 point_transactions |
| Доступ | R через SQL (бот уже подключён к Neon) |

### 4.4. ЦД → Points Engine

| Аспект | Описание |
|--------|----------|
| Направление | ЦД → Points Engine (квалификация для множителя) |
| Данные | qualification_level (Random/Practicing/Systematic/Disciplined/Proactive) |
| Источник | development.digital_twin_state или ЦД-проекция в Neon |
| Частота | При каждом calculate_points() — чтение текущей квалификации |

### 4.5. Ory → Points Engine

| Аспект | Описание |
|--------|----------|
| Направление | Ory → Points Engine (идентификация) |
| Данные | ory_id (UUID) — единственный идентификатор участника |
| Связь | user_uuid во всех таблицах = ory_id |
| При двух Ory | canonical_ory_id через identity_links (см. 02-cross-region) |

### 4.6. Metabase → Points Engine

| Аспект | Описание |
|--------|----------|
| Направление | Metabase ← Points Engine (аналитика) |
| Дашборды | Распределение баллов, top earners, конверсия баллов→скидки |
| Доступ | R ко всем таблицам finance.* |

---

## 5. Зависимости реализации

```
WP-109 Ф1 (LMS bulk sync) ✅ done
  └→ WP-109 Ф4 (Readiness Gate) — pending, активировать с WP-121
  └→ WP-109 Ф5 (Event Bus: pg_notify + Dispatcher) — pending
       └→ WP-121 Ф2 (calculate_points — первый подписчик)

WP-183 (CRM-сервис) — in_progress (приоритет №1, 2 недели)
  └→ WP-121 Ф4 (интеграция Billing → spent)

WP-187 (Ory Gateway) — in_progress
  └→ WP-121: ory_id как идентификатор во всех таблицах

WP-215 (разделение РФ/мир) — in_progress
  └→ 02-cross-region-architecture.md (source_region, outbox, federation)
```

---

## 6. API (предварительный)

### Points Engine (внутренний)

| Метод | Описание | Вызывает |
|-------|----------|----------|
| `calculate_points(event)` | Начислить баллы за событие | Dispatcher (Event Bus) |
| `replay(from_date, to_date)` | Пересчитать за период | Админ / cron |
| `get_balance(ory_id)` | Баланс участника | Бот, Billing |
| `get_history(ory_id, limit)` | История начислений | Бот |
| `spend(ory_id, amount, ref)` | Списать баллы | Billing Service |

### Бот

| Команда | Что делает |
|---------|-----------|
| `/points` | Баланс + последние начисления |
| `/points detail` | Подробная история с фильтрами |
| `/buy_with_points` | Оплата баллами (→ Billing Service) |

---

*Создано: 2026-04-09. WP: 121, 109, 183, 187, 215.*
