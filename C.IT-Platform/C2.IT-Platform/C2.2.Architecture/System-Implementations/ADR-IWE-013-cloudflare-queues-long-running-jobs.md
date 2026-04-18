---
id: ADR-IWE-013
title: "Cloudflare Queues для long-running background jobs в MCP-воркерах"
status: accepted
date: 2026-04-18
deciders: [Tseren]
context: "WP-187 Ф-K.1 (ctx.waitUntil) умер на 30-секундном grace period при reindex 468 файлов; Ф-K.1.2 перенесена на Queues"
related:
  pack: [DP.ARCH.001, DP.SC.112]
  uses: [ADR-IWE-004, ADR-IWE-012]
  supersedes_pattern_in: [ADR-IWE-006]
  realized_by: [WP-187]
family: F8
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-013: Cloudflare Queues для long-running background jobs

## 1. Контекст

MCP-воркеры (pk-mcp, knowledge-mcp, dt-mcp) работают на Cloudflare Workers. Некоторые задачи долгие:

- **Full-source reindex** (pk-mcp): 468 файлов × OpenAI embedding + pgvector INSERT = ~10-15 мин.
- **Auto-initial indexing** после OAuth callback (Ф-K.2): тот же паттерн.
- **Pack scaffold** (knowledge-mcp, будущее): десятки файлов.
- **DT ingest** (dt-mcp, будущее): batch-расчёт индикаторов.

Cloudflare Worker HTTP-обработчик должен завершиться максимум через ~30 сек. Два варианта продолжить работу после HTTP-ответа:

| Механизм | Ограничение |
|----------|-------------|
| `ctx.waitUntil(promise)` | **Hard kill ~30 сек** после HTTP-ответа. Документация говорит 30 сек grace period, не «до 30 мин CPU». |
| Cloudflare Queues | До 30 сек **на каждое queue-сообщение**, retries встроены, DLQ, at-least-once. |
| Durable Objects | До 30 мин CPU на объект. На Free-tier с апр 2025. Сложнее (миграция, binding). |
| Cloudflare Workflows | Durable state-machine. Overkill для простого fan-out. |
| Внешний runner (Railway) | Выходим из Cloudflare-периметра. |

**Инцидент Ф-K.1 (17 апр):** ArchGate Q1 (17 апр) считал `ctx.waitUntil` достаточным для 30-минутного reindex. E2E 18 апр на `DS-my-strategy` (468 файлов) провалился: 2 job'а застряли в `running` (4fa20f3b — 4335 сек, dba58dcd — 325 сек, 32/468 вставлено). Wrangler tail показал:
```
(warn) waitUntil() tasks did not complete within the allowed time
after invocation end and have been cancelled
```

Worker умер тихо, без throw, без финального UPDATE — job'ы остались вечно `running` без heartbeat. Помечены failed вручную.

## 2. Рассмотренные варианты

ArchGate Ф-K.1.2 (18 апр, ЭМОГССБ, критичны Э+М+Г):

| Характеристика | A. Cloudflare Queues | B. Durable Objects | C. Railway runner |
|----------------|----------------------|---------------------|---------------------|
| **Э**волюционируемость | ✅ producer/consumer развязаны | ⚠️ binding + DO migration | ⚠️ новый runtime surface |
| **М**асштабируемость | ✅ до 10K msg/sec, fan-out N consumers | ✅ 1 DO per (user, source) | ⚠️ cron-polling ≠ push |
| **О**бучаемость | ⚠️ новый concept (queues), но ≤200 строк | ❌ DO migration — кривая обучения | ✅ стандартный Node.js cron |
| **Г**енеративность | ✅ паттерн переиспользуется (auto-init, DT ingest, scaffold) | ⚠️ per-case namespace | ❌ каждый MCP получает свой runner |
| **С**корость | ✅ <100ms producer ответ | ✅ <100ms | ⚠️ latency до 1 мин (cron 1/min) |
| **С**овременность | ✅ CF-native 2022+, at-least-once, DLQ | ✅ CF-native 2021+ | ⚠️ classic pattern |
| **Б**езопасность | ✅ encryption in transit, Cloudflare-periметр | ✅ тот же | ⚠️ Railway ≠ CF perimeter (WP-228 §3) |

**Фактчек субагентом:**
- Cloudflare Queues на Free-tier — **10K operations/day** (не 1M/мес как думали изначально), 1M/мес — Paid $5/мес.
- Durable Objects на Free-tier **с апреля 2025** (раньше требовали Workers Paid).
- 3 ключевые грабли Queues: idempotency (at-least-once → дубли), per-message ack/retry (`msg.ack()` / `msg.retry()`), отсутствие локальной эмуляции (miniflare).

Вердикт: **вариант A — Cloudflare Queues**. DO бьёт на Обучаемости и Генеративности (создаёт namespace per use-case вместо одного паттерна). Railway бьёт на Стратегии (WP-228 §3 «Cloudflare-first»).

## 3. Решение

**Принят вариант A — Cloudflare Queues для long-running background jobs внутри MCP-воркеров.**

Паттерн: **producer во входящем HTTP-запросе → queue messages (batches) → consumer в том же Worker → инкрементальный UPDATE прогресса в БД → completion detection через счётчик батчей.**

### 3.1. Поток (на примере pk-mcp full-source reindex)

```
1. AI-агент → pk-mcp: personal_reindex_source(source="X")
2. pk-mcp (HTTP handler):
   a. startReindexJob: SELECT cooldown (60s window)
   b. INSERT knowledge.reindex_jobs (user_id, source, status='pending')
   c. listMdFilesViaTrees(env, ctx, source) → paths (~N файлов)
   d. Split: batches of 10 → ReindexBatchMessage[]
   e. UPDATE reindex_jobs SET total=N, expected_batches=M, status='running',
      last_heartbeat_at=NOW()
   f. env.REINDEX_QUEUE.sendBatch(batches)
   g. Ответ клиенту: { job_id, status: 'running', message: '... M batch(es)' }
3. Cloudflare Queue (REINDEX_QUEUE):
   - max_batch_size: 10 (файлов в одном сообщении)
   - max_batch_timeout: 5 сек
   - max_retries: 3
   - dead_letter_queue: reindex-dlq
4. Consumer (export default.queue в том же pk-mcp Worker):
   a. Для каждого msg: проверить status job'а ('running'?)
   b. reindexFiles(env, { source, files, user_id }) — внутри: hash check, embedding, INSERT ON CONFLICT DO NOTHING
   c. UPDATE reindex_jobs SET processed+=P, skipped+=S, deleted+=D,
      completed_batches+=1, last_heartbeat_at=NOW(), errors+=[...]
   d. Если completed_batches = expected_batches → status='succeeded', finished_at=NOW()
   e. msg.ack()   // успех → ack
   f. msg.retry() // исключение → retry (до max_retries), потом → DLQ
5. Клиент (опционально): poll reindex_status(job_id) каждые 30 сек
```

### 3.2. Миграция БД (010)

Три поля для heartbeat + batch accounting:

```sql
ALTER TABLE knowledge.reindex_jobs
  ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS expected_batches INT,
  ADD COLUMN IF NOT EXISTS completed_batches INT NOT NULL DEFAULT 0;

-- Watchdog (stale detection): раз в 5 мин SELECT running jobs с протухшим heartbeat.
CREATE INDEX idx_reindex_jobs_running_heartbeat
  ON knowledge.reindex_jobs (last_heartbeat_at)
  WHERE status = 'running';
```

**Почему expected_batches, а не `processed = total`:** at-least-once → `msg.retry()` может повторно инкрементить `processed`. Счётчик батчей (инкрементируется только при успешном ack) даёт детерминированный критерий завершения.

### 3.3. wrangler.toml биндинг

```toml
[[queues.producers]]
queue = "reindex"
binding = "REINDEX_QUEUE"

[[queues.consumers]]
queue = "reindex"
max_batch_size = 10
max_batch_timeout = 5
max_retries = 3
dead_letter_queue = "reindex-dlq"
```

### 3.4. Идемпотентность

Дубликаты from at-least-once защищены на двух уровнях:

1. **Hash check в reindexFiles:** `SELECT hash FROM knowledge.documents ... LIMIT 1` — если hash совпадает, файл `skipped` (нет embedding, нет INSERT).
2. **INSERT ON CONFLICT:** `ON CONFLICT (filename, source, COALESCE(user_id, '')) DO NOTHING`.

При повторной доставке батча `processed` увеличится на 0, `skipped` — на N, embedding'ов не будет. Это приемлемо для счётчиков, но означает: **`processed + skipped` может превысить `total`** на ретраях. Для детекции завершения используется `completed_batches = expected_batches`, а не `processed = total`.

### 3.5. Poison pill handling

Один плохой файл в батче из 10:
- Внутри `reindexFiles`: try/catch на файл → `errors.push(msg)`, остальные 9 проходят нормально.
- Батч считается обработанным → `msg.ack()`.
- **Вся ошибка попадает в `errors[]` jobа**, но НЕ блокирует остальной прогресс.

Если `reindexFiles` упал целиком (например, OpenAI 5xx на первом файле без catch выше) → `msg.retry()`. После `max_retries=3` → `reindex-dlq`. Сейчас DLQ инспектируется вручную.

### 3.6. Observability

- **Логи consumer:** один JSON per msg (`phase: consume_ok | consume_err | consume_skip`, `job_id`, `source`, `files`, `processed`, `skipped`, `elapsed_ms`, `attempt`). В wrangler tail видны по `--search phase`.
- **Heartbeat:** `last_heartbeat_at` обновляется каждым успешным ack. Видно в БД `SELECT ... FROM knowledge.reindex_jobs WHERE status='running'`.
- **Клиентский polling:** `reindex_status(job_id)` возвращает `processed/skipped/deleted/total + expected_batches/completed_batches + errors[]`.

### 3.7. Watchdog (отдельная фаза)

Cron-trigger раз в 5 мин:

```sql
UPDATE knowledge.reindex_jobs
  SET status = 'failed', finished_at = NOW(),
      errors = COALESCE(errors, '[]'::jsonb) || '["heartbeat timeout"]'::jsonb
  WHERE status = 'running'
    AND last_heartbeat_at < NOW() - INTERVAL '2 minutes'
    AND (expected_batches IS NULL OR completed_batches < expected_batches);
```

Защита от застрявших job'ов: если consumer умер / queue недоступен / БД недоступна для финального UPDATE — heartbeat перестаёт обновляться, watchdog через 2 мин пометит failed. Реализация отложена (Ф-K.1.3 или WP-244 observability).

## 4. Последствия

### Плюсы

- **Долгие задачи возможны на Cloudflare-периметре** (не нужен Railway runner).
- **Инкрементальный прогресс**: клиент видит `processed/total` и может оценить ETA.
- **Poison-pill изоляция**: один плохой файл не блокирует job.
- **Паттерн переиспользуется**: Ф-K.2 auto-init, dt-mcp ingest, knowledge-mcp Pack scaffold — тот же queue + consumer + jobs-таблица.
- **Retries + DLQ бесплатно**: транзиентные ошибки (OpenAI 5xx, Neon timeout) сами пересылаются.

### Минусы

- **Новый концепт** (queues) — требует обучения команды.
- **Нет локальной эмуляции** (miniflare): тестировать только на real Cloudflare в dev environment.
- **At-least-once → дубли**: каждый consumer обязан быть идемпотентным. Требование проектирования.
- **Free-tier 10K ops/day:** при ~50 batch/job × 20 reindex/day/user × N пользователей можно упереться. Мониторить; до Paid $5/мес — запас.

### Связи

- **Заменяет в pk-mcp:** `ctx.waitUntil(runReindexJob)` → `env.REINDEX_QUEUE.sendBatch` + `export default.queue`.
- **Не заменяет в других ADR:** ADR-IWE-006 (async write pattern) использует Neon `write_queue` + background Worker (коммиты в GitHub, 1-3 сек/запись). Это другой use-case — не долгие batch-задачи, а series of short commits. Queues для ADR-006 overkill.
- **Разблокирует:** Ф-K.2 (auto-initial indexing при OAuth), dt-mcp ingest, knowledge-mcp Pack scaffold.

## 5. Критерии отмены ADR

- Cloudflare Queues станет Paid-only (сейчас 10K/day Free) → пересмотреть (возможно DO, уже на Free).
- Consumer-время перестанет помещаться в 30 сек на batch даже с batch=1 → перейти на Durable Objects (30 мин CPU).
- Понадобится sync-response с результатом всего job'а (не polling) → пересмотреть (HTTP keepalive до 100 сек доступен).

## 6. Реализация

**Первый use-case:** `personal_reindex_source` в pk-mcp (WP-187 Ф-K.1.2).

Коммиты:
- `personal-knowledge-mcp@68faf5f` — queue producer+consumer, миграция 010 intro, ACK/retry handler.
- `personal-knowledge-mcp@d589d97` — fix encodeURIComponent в GitHub Contents API.
- Cloudflare deploy: `00fff5a3`, `6e760f56`.

E2E доказательство (18 апр, 469 файлов DS-my-strategy): `succeeded` за 12м 43с, heartbeat обновлялся, incremental progress виден через polling. 8 errors (1 OpenAI 500 + 7 URL-encoding bug — фикс уже задеплоен).
