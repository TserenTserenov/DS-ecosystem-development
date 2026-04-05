---
id: ADR-IWE-006
title: "Async Write Pattern — очередь записи в GitHub"
status: accepted
date: 2026-04-05
deciders: [Tseren]
context: "WP-73 Phase 2 — UX записи через Personal Knowledge MCP: GitHub API медленный (1-3 сек)"
related:
  pack: [DP.D.036]
  uses: [ADR-IWE-004, ADR-IWE-005]
  realized_by: [WP-187]
family: F6
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-006: Async Write Pattern — очередь записи в GitHub

## 1. Контекст

Personal-knowledge-mcp (L4) записывает в GitHub-репо пользователя через Installation Token (ADR-IWE-004). GitHub Contents API — синхронный HTTP: `PUT /repos/{owner}/{repo}/contents/{path}` занимает 1-3 секунды (сеть + SHA-расчёт + коммит).

**Проблема:** Если MCP ждёт завершения коммита синхронно, AI-агент блокируется на 1-3 сек при каждой записи. При серии записей (capture → 3-5 файлов) = 5-15 сек ожидания. UX страдает.

**Контексты записи (оперативка 5 апр):** личный, проектный, публичный — разные репо, один способ работы. Паттерн записи должен быть единым для всех трёх контекстов.

## 2. Рассмотренные варианты

| Вариант | Латентность для клиента | Гарантия записи | Сложность |
|---------|------------------------|-----------------|-----------|
| A. Синхронный (текущий) | 1-3 сек | Гарантирована (ответ = коммит) | Минимальная |
| **B. Queue + Background (принят)** | <100ms | Eventually consistent (~5 сек) | Средняя |
| C. Optimistic + Rollback | <100ms | Требует компенсации при ошибке | Высокая |

## 3. Решение

**Принят вариант B — Queue + Background Commit.**

### 3.1. Поток

```
1. AI-агент → personal-knowledge-mcp: write(path, content)
2. MCP:
   a. Валидирует: repo в списке разрешённых (ADR-IWE-004 §3.5)
   b. Кладёт задание в write_queue (Neon)
   c. Отвечает клиенту: { status: "queued", queue_id, eta_seconds: 5 }
   d. INSERT ingest_event (ADR-IWE-005) с triggered_by: "ai_agent"
3. Background Worker (тот же CF Worker, scheduled или Durable Object):
   a. Читает из write_queue (FIFO per user)
   b. Генерирует Installation Token (1h TTL)
   c. PUT GitHub Contents API
   d. При успехе: UPDATE write_queue SET status = 'committed', commit_sha = ?
   e. Переиндексация embeddings (delta ingest)
   f. При ошибке: retry (до 3 раз, exponential backoff)
4. Клиент (опционально): poll GET /write-status/{queue_id}
   → { status: "committed", commit_sha, commit_url }
```

### 3.2. Таблица write_queue

```sql
CREATE TABLE write_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,           -- Ory UUID
  repo TEXT NOT NULL,              -- "owner/repo"
  path TEXT NOT NULL,              -- "inbox/note.md"
  content TEXT NOT NULL,           -- Содержимое файла
  operation TEXT NOT NULL DEFAULT 'update', -- create | update | delete
  status TEXT NOT NULL DEFAULT 'queued',    -- queued | processing | committed | failed
  commit_sha TEXT,                 -- Заполняется после коммита
  error_message TEXT,              -- При failed
  retry_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  committed_at TIMESTAMPTZ,
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES ... -- Ory identity
);

-- RLS: пользователь видит только свои записи
ALTER TABLE write_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_own ON write_queue
  USING (user_id = current_setting('app.user_id'));

-- Индекс для Background Worker
CREATE INDEX idx_queue_pending ON write_queue (created_at)
  WHERE status = 'queued';
```

### 3.3. Батчинг

При серии записей (3-5 файлов за <10 сек) Background Worker объединяет в один коммит:

```
1. Worker просыпается (каждые 2 сек или по pg_notify)
2. SELECT * FROM write_queue WHERE user_id = ? AND status = 'queued' ORDER BY created_at
3. Если >1 записи и все в один repo:
   a. Один Installation Token
   b. Один commit с несколькими файлами (Tree API)
   c. UPDATE всех записей SET status = 'committed', commit_sha = ?
4. Если записи в разные repo — по одному коммиту на repo
```

**Выигрыш:** 5 файлов = 1 коммит вместо 5. Меньше нагрузка на GitHub API, чище git history.

### 3.4. Режимы записи

| Режим | Когда | Поведение |
|-------|-------|-----------|
| `async` (default) | Обычная работа | Queue + background. Ответ <100ms |
| `sync` | Критические записи (Pack) | Ждёт коммита. Ответ 1-3 сек |

AI-агент указывает режим: `write(path, content, { mode: "async" })`. По умолчанию async.

**Когда sync:** propose_capture с подтверждением пользователя (пользователь ожидает результата).

### 3.5. Обработка ошибок

| Ошибка | Retry? | Действие |
|--------|--------|---------|
| 409 Conflict (SHA mismatch) | Да (1 раз) | Перечитать текущий SHA, повторить PUT |
| 403 Forbidden | Нет | Status = 'failed'. Installation отозвана? Уведомить пользователя |
| 422 Unprocessable | Нет | Status = 'failed'. Невалидный path или content |
| 5xx / timeout | Да (до 3 раз) | Exponential backoff: 2s, 4s, 8s |
| Все retry исчерпаны | — | Status = 'failed'. pg_notify → уведомление через бот |

### 3.6. Consistency гарантии

**Проблема:** между ответом «queued» и фактическим коммитом — окно ~5 сек. Если пользователь читает файл в этом окне, он увидит старую версию.

**Решение: read-your-writes.**
- При `search` и `get_document`: проверить write_queue на pending записи для этого user_id + path
- Если есть pending — вернуть content из очереди (не из GitHub/embeddings)
- После коммита — embeddings обновляются, read-your-writes больше не нужен

## 4. Связь с архитектурой

| Решение | Связь |
|---------|-------|
| ADR-IWE-004 (GitHub App) | Installation Token генерируется Background Worker, не на hot path |
| ADR-IWE-005 (ingest_event) | Event записывается при постановке в очередь (немедленно), не при коммите |
| ADR-IWE-003 (Backend Interface) | write tool возвращает `{ status: "queued" }` вместо `{ sha }` |
| ADR-009 (Activity Hub) | ingest_event немедленный — Activity Hub не ждёт коммита |
| DP.D.036 (BYOB) | Async write = единый паттерн для всех контекстов (личный, проектный, публичный) |

## 5. Последствия

**Положительные:**
- UX: <100ms вместо 1-3 сек на каждую запись
- Батчинг: меньше коммитов, чище history
- Единый паттерн для всех трёх контекстов (оперативка 5 апр)
- GitHub API rate limit: меньше запросов (батчинг)

**Отрицательные:**
- Eventually consistent: окно ~5 сек между «сохранено» и фактическим коммитом
- Дополнительная таблица write_queue в Neon
- Сложность read-your-writes (проверка очереди при чтении)

**Риски:**
- Background Worker падает — записи застревают в очереди. Митигация: healthcheck на `SELECT COUNT(*) FROM write_queue WHERE status = 'queued' AND created_at < NOW() - INTERVAL '1 minute'`. Алерт если >0
- Пользователь параллельно редактирует файл в VS Code — конфликт SHA. Митигация: 409 retry с перечитыванием SHA
