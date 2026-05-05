---
type: technical-analysis
title: "Neon — что мы используем и что теряем при отказе"
status: draft-for-discussion
created: 2026-05-05
related: WP-285, WP-253
audience: Андрей (архитектор), Паша (инженер), Тсерен
---

# Neon — анализ зависимости и стоимости отказа

> **Контекст:** Встреча 13 (5 мая) приняла Р-TrackB-7 — в коде писать тип Postgres, не Neon. Документ — что это значит на практике, можем ли отказаться, что теряем.

---

## 1. Что у нас сейчас на Neon

### Используемые БД (по DP.ARCH.004 v2.4.x)

12 entity БД + 3 special:

| # | БД | Назначение | Объём (оценка) |
|---|----|-----------|----------------|
| 1 | platform | Identity, accounts, OAuth tokens | ~50 MB |
| 2 | learning | Курсы, прогресс, посты | ~500 MB (растёт быстро) |
| 3 | persona | PII, профили, identity claims | ~100 MB |
| 4 | indicators | RCS, baselines, метрики | ~200 MB |
| 5 | subscription | subscription_grants, БР | ~20 MB |
| 6 | finance | finance_payments, YooKassa | ~50 MB |
| 7 | security | RLS-логи, токены, ключи | ~30 MB |
| 8 | health | internal_metrics, observability | ~1 GB (high-volume writes) |
| 9 | knowledge | concepts, embeddings (pgvector) | ~5 GB (растёт с контентом) |
| 10 | content | posts, comments, captures | ~2 GB |
| 11 | rewards | balls, активные действия | ~100 MB |
| 12 | events | event-gateway domain_event log | ~10 GB (append-only, growing) |

**Текущая стоимость Neon (оценка):** Free tier недостаточен → Pro tier ~$19/мес × N инстансов или Scale tier $69/мес. По объёму ~$50–100/мес сейчас.

### Драйверы и пакеты в коде

| Файл/Сервис | Импорт | Использует | Заменяемость |
|-------------|--------|------------|--------------|
| `gateway-mcp/src/index.ts` (12+ мест) | `import { neon } from "@neondatabase/serverless"` | HTTP-драйвер для CF Workers | `postgres.js` через HTTP-прокси (если CF) или `pg` (если VPS) |
| `gateway-mcp/src/backend-registry.ts` | то же | то же | то же |
| `gateway-mcp/src/utils/db.ts` | то же | то же | то же |
| `knowledge-mcp/src/index.ts` | то же | то же | то же |
| `knowledge-mcp/src/rls.ts` | `neonConfig`, `Pool` from `@neondatabase/serverless` | WebSocket-пул для транзакций SET LOCAL | `pg.Pool` если уйдём от CF |
| `event-gateway/src/db.ts` | `neon`, `NeonQueryFunction` | то же | то же |
| `payment-receiver/src/{db,index}.ts` | `neon` | то же | то же |
| `personal-knowledge-mcp/src/index.ts` | `neon` | то же | то же |
| `guides-mcp/src/index.ts` | `neon` | то же | то же |
| `knowledge-mcp/scripts/migrate-*.ts` | `neon` | миграции | `pg` (это Node.js скрипты, не CF Workers) |
| `aist_bot` (Python) | `asyncpg` | стандартный Postgres-драйвер | без изменений — `asyncpg` работает с любым Postgres |

**SQL-фич Neon-специфичных:** не найдено. Все запросы стандартный Postgres.
**Branching API:** не используется.
**Neon-расширения:** не используются (pgvector — стандартное, не Neon-специфично).
**Connection pooling Neon:** используется через `-pooler.` суффикс в DSN — стандартный PgBouncer transaction-mode, заменяется на свой PgBouncer/PgCat.

---

## 2. Что Neon даёт «бесплатно» в архитектуре

| Фича | Что делает | Чем заменяется при self-hosted |
|------|------------|--------------------------------|
| **Auto-suspend** | Compute спит когда нет запросов; cold-start ~1 сек. Платим только за активные часы | — (всегда платим за сервер) |
| **Storage-compute separation** | Storage платим отдельно от compute; compute может масштабироваться | — (на VPS они слиты) |
| **Branching** | DB-ветки как git: создал ветку → копия данных copy-on-write → тестировал → удалил | Логические бэкапы + restore в отдельный инстанс (медленно, ручная работа) |
| **Point-in-Time Recovery** | Восстановление на любой момент за последние 7-30 дней | WAL-archiving + pgBackRest / wal-g (нужно настроить) |
| **Auto-scale compute** | CPU/RAM растут автоматически при нагрузке | Ручной resize ноды + рестарт |
| **Connection pooling** | PgBouncer transaction-mode встроен в `-pooler.` endpoint | Свой PgBouncer / PgCat (~5 мин на сервере) |
| **Monitoring dashboards** | Latency, connections, slow queries в UI Neon | pg_stat_statements + Grafana / Prometheus (нужно поднять) |
| **Daily backups** | Автоматические, без настройки | pg_basebackup + cron + S3 (нужно настроить) |
| **Read replicas** | За один клик в одном регионе | Streaming replication + ручная настройка |
| **HTTP/WebSocket transport** | Работает в Cloudflare Workers (нет TCP) | Через Hyperdrive (CF) или pg-proxy (Supabase ставит supavisor) |

---

## 3. Стоимость отказа от Neon — оценка трудозатрат

### Если переходим на self-hosted Postgres (Hetzner/Vultr VPS)

| Задача | Время | Зависимость |
|--------|-------|-------------|
| Замена `@neondatabase/serverless` на `pg` в Node.js скриптах (миграции, одноразовые) | 4h | низкая |
| Замена `neon()` на `postgres.js` в Track B новых сервисах | 2h на сервис × 7 сервисов = 14h | средняя |
| **Решение:** оставить CF Workers с Neon HTTP-драйвером? | 0h (если оставить) | — |
| Установка и настройка PostgreSQL на VPS | 3h | низкая |
| Настройка PgBouncer/PgCat | 2h | низкая |
| pgBackRest + WAL archiving + S3 backup | 6h | средняя |
| Monitoring (pg_stat_statements + Prometheus exporter + Grafana) | 4h | средняя |
| Streaming replication для HA | 8h | высокая |
| Восстановление из backup тренировка | 2h | низкая |
| **Итого** | **~45h** | |

### Если переходим на managed Postgres в облаке (Cloud SQL / RDS)

| Задача | Время | Зависимость |
|--------|-------|-------------|
| Создание Cloud SQL / RDS инстансов (12 БД на 1 инстанс) | 2h | низкая |
| Замена DSN в коде (NEON_PROD_BASE → CLOUDSQL_DSN) | 1h | низкая |
| Connection pool (Cloud SQL Proxy / RDS Proxy) | 2h | низкая |
| HTTP-bridge для CF Workers — через Hyperdrive / Supabase pgRest / самописный | 6h | средняя |
| Backup настройки (включаются галочкой) | 0.5h | низкая |
| **Итого** | **~12h** | |

---

## 4. Сценарии — что делать с Neon

### Сценарий 1: Оставить Neon как есть для Track A, новое только в Track B

**Что:** 12 текущих БД остаются на Neon. Новые БД для Track B (если будут) — на Hetzner/Cloud SQL. Постепенная миграция при необходимости.

**Плюсы:** Никаких миграций сейчас. Track A не трогаем.
**Минусы:** Track B зависит от Neon до миграции (если CF Workers продолжают использовать Neon БД).

### Сценарий 2: Полный переход с Neon на managed Postgres в облаке

**Что:** Cloud SQL (если GKE) или RDS (если EKS). Миграция через `pg_dump`/`pg_restore` или logical replication.

**Плюсы:** Унифицированная инфраструктура с compute. Все managed-фичи provider'а. Нет Neon в зависимостях.
**Минусы:** ~12h работы + downtime на миграцию или logical replication. Cloud SQL/RDS дороже Neon Pro в 1.5-2× на сопоставимых объёмах.

### Сценарий 3: Полный переход на self-hosted Postgres на Hetzner

**Что:** PostgreSQL 16 на Hetzner CX32, 12 баз на одном инстансе. Свой backup + monitoring.

**Плюсы:** Самое дешёвое (~$13/мес vs $50-100 Neon). Полный контроль. EU GDPR.
**Минусы:** ~45h работы. Берём ответственность за бэкапы, апгрейды, безопасность.

### Сценарий 4: Гибрид — Neon EU для Track B, миграция Track A позже

**Что:** Создать новые Neon-проекты в EU-регионе (`aws-eu-central-1`) для Track B. Track A остаётся в текущем регионе.

**Плюсы:** Никаких миграций кода. Минимум работы. EU-residency для Track B.
**Минусы:** Платим Neon × 2 (RU и EU). Зависимость от Neon сохраняется.

---

## 5. Рекомендация по Neon

### Если GKE Autopilot выбрана как инфраструктура

**→ Сценарий 2: Cloud SQL.** Унифицируем БД с compute. Ставим Hyperdrive (CF) для CF Workers → Cloud SQL. Миграция через logical replication (downtime минут 15).

### Если Hetzner выбран как инфраструктура

**→ Сценарий 3 для нового, Сценарий 1 для старого.** Self-hosted Postgres на Hetzner для всех новых БД Track B. Track A на Neon до передачи Ильшату — он сам решит, мигрировать или нет.

### Если Vultr выбран

**→ Сценарий 4: гибрид с Neon EU.** Vultr Managed Database дорогой, self-hosted на Vultr — невыгодно. Neon EU отдельный проект для Track B, ~$25-50/мес.

---

## 6. Архитектурное правило (Р-TrackB-7)

В **коде и документах** писать:

```typescript
// ✅ правильно
import postgres from "postgres";
const sql = postgres(env.DATABASE_URL);

// ❌ неправильно (привязка к Neon)
import { neon } from "@neondatabase/serverless";
const sql = neon(env.DATABASE_URL);
```

**Исключение:** CF Workers без Hyperdrive/Cloud SQL Proxy. Там `@neondatabase/serverless` остаётся как HTTP-транспорт, но в комментарии — пометить «driver-only, schema is plain Postgres».

В **архитектурных описаниях** (DP.ARCH.004, ADR'ы) — `Postgres`, не `Neon`. Neon упоминается только в реализационном слое:

```markdown
## Хранение
**Тип:** Postgres 16 с pgvector
**Реализация:** Neon Pro (текущая) → Cloud SQL EU (Track B target)
**DSN:** `NEON_PROD_BASE` env var
```

---

## 7. Открытые вопросы

| # | Вопрос | Кто решает |
|---|--------|------------|
| 1 | Текущий регион Neon — RU или EU? Если RU — Track B пользователи нарушают GDPR | Андрей |
| 2 | Какие БД у нас сейчас фактически в Neon (vs планируемые)? | Паша |
| 3 | Реальные расходы на Neon в апреле 2026? | Тсерен (биллинг) |
| 4 | Hyperdrive vs Cloud SQL Proxy для CF Workers → Cloud SQL — что лучше? | Андрей |
| 5 | Готовы ли инвестировать 45h в self-hosted Postgres ради $30/мес экономии? | Тсерен (бюджет vs время) |
