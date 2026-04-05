---
id: ADR-IWE-005
title: "ingest_event: Personal Knowledge MCP → Activity Hub"
status: accepted
date: 2026-04-05
deciders: [Tseren, Олег]
context: "WP-73 Phase 2 — Activity Hub должен видеть L4-события (записи в личные репо)"
related:
  pack: [DP.ARCH.003, DP.D.036]
  uses: [ADR-009, ADR-IWE-003, ADR-IWE-004]
  realized_by: [WP-109]
family: F6
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-005: ingest_event — Personal Knowledge MCP → Activity Hub

## 1. Контекст

Activity Hub (ADR-009) — платформенный журнал событий. Сейчас в него пишут бот и dt-collect (cron). Personal-knowledge-mcp (L4) умеет писать в GitHub-репо пользователя (ADR-IWE-004), но Activity Hub об этих записях не знает.

**Проблема:** ЦД (DP.ARCH.003) не видит, что пользователь работал со своим Pack/DS через MCP. Нет данных для проекций (активность, прогресс, когнитивный профиль). WP-109 (Activity Hub v2) не может подключить Personal Knowledge как источник.

**Ограничение из оперативки 5 апр:** Gateway = прозрачный прокси (авторизация + проброс). Gateway НЕ фильтрует, НЕ преобразует, НЕ генерирует side effects. Следовательно, ingest_event вызывается самим MCP-сервером, не Gateway.

## 2. Решение

**Personal-knowledge-mcp при каждой мутации (write, propose_capture с auto-accept) вызывает `ingest_event()` в Activity Hub напрямую — минуя Gateway.**

### 2.1. Поток

```
1. AI-агент → Gateway → personal-knowledge-mcp: write(path, content)
2. personal-knowledge-mcp:
   a. Записывает в GitHub (ADR-IWE-004)
   b. Ставит в очередь переиндексацию (embeddings)
   c. POST Activity Hub: ingest_event(event)    ← НОВОЕ
3. Ответ клиенту: { sha, commit_url, indexed: true }
```

### 2.2. Формат события

```typescript
interface IngestEvent {
  // Обязательные
  event_type: "knowledge_write" | "knowledge_capture" | "knowledge_delete";
  user_id: string;          // Ory UUID (из JWT)
  timestamp: string;        // ISO 8601
  source_system: string;    // "personal-knowledge-mcp"

  // Контекст записи
  repo: string;             // "owner/repo-name"
  path: string;             // "inbox/fleeting-notes.md"
  operation: "create" | "update" | "delete";
  bytes_changed: number;    // Размер diff

  // Опциональные (для проекций ЦД)
  source_type?: string;     // "pack" | "ds" | "fmt"
  commit_sha?: string;      // SHA коммита в GitHub
  triggered_by?: string;    // "ai_agent" | "webhook" | "manual"
}
```

### 2.3. Транспорт

| Вариант | Механизм | Латентность | Надёжность |
|---------|----------|-------------|------------|
| **A. Прямой INSERT (принят)** | personal-knowledge-mcp → Neon `INSERT INTO development.user_events` | <10ms | Транзакция с основной записью |
| B. pg_notify | NOTIFY → слушатель | ~50ms | At-most-once |
| C. HTTP POST | Отдельный эндпоинт Activity Hub | ~100ms | Зависит от сети |

**Принят вариант A** — прямой INSERT. Обоснование:
- Personal-knowledge-mcp уже подключён к Neon (для embeddings, ADR-IWE-001)
- INSERT в ту же БД = одна транзакция, гарантированная доставка
- Нет дополнительного сетевого хопа
- pg_notify используется Activity Hub для уведомления downstream-подписчиков (ADR-009), но это уже после записи

### 2.4. Кто вызывает ingest_event

| Система | Пишет ingest_event? | Почему |
|---------|---------------------|--------|
| **personal-knowledge-mcp** | Да (этот ADR) | Write path: запись в GitHub + embeddings + event |
| **Gateway** | Нет | Прозрачный прокси (решение 5 апр) |
| **knowledge-mcp (L2)** | Нет | Read-only, нет мутаций |
| **digital-twin-mcp** | Нет | Read-only потребитель. Writer = R28 Профилировщик |
| **Бот** | Да (существующий) | Пишет события через `log_event()` |
| **dt-collect** | Да (существующий) | Cron: собирает события из LMS/Клуба |

## 3. Связь с архитектурой

| Решение | Связь |
|---------|-------|
| ADR-009 (Activity Hub = платформенный журнал) | Этот ADR расширяет ADR-009 на L4-события |
| ADR-IWE-003 (Backend Interface) | write/propose_capture — инструменты контракта, вызывающие ingest_event |
| ADR-IWE-004 (GitHub App) | Запись в GitHub триггерит ingest_event |
| DP.ARCH.003 §4.4 (Channel-Agnostic Events) | ingest_event следует принципу: событие не зависит от канала |
| DP.ARCH.001 #12 (Интерфейсы через обработку) | L4 MCP (Слой 2Б) пишет в Activity Hub (Слой 1), не Gateway (Слой 3) |
| WP-109 (Activity Hub v2) | Этот ADR разблокирует Ф3: подключение Personal Knowledge как источника |

## 4. Последствия

**Положительные:**
- ЦД видит всю активность пользователя (не только бот/LMS, но и MCP-записи)
- Единый event store для всех источников (ADR-009)
- Прозрачность Gateway сохранена (side effects — ответственность MCP)
- Одна транзакция: GitHub write + embeddings update + event insert

**Отрицательные:**
- personal-knowledge-mcp усложняется (дополнительный INSERT при каждой мутации)
- Coupling: MCP знает о таблице `development.user_events` (митигация: shared SQL-функция `insert_event()`)

**Риски:**
- Event storm при массовой синхронизации (например, первый ingest 100+ файлов). Митигация: batch events с `event_type: "knowledge_bulk_ingest"`, один event на batch
