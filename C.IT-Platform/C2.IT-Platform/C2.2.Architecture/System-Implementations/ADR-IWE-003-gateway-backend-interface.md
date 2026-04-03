---
id: ADR-IWE-003
title: "Gateway Backend Interface — контракт MCP-серверов за Gateway"
status: accepted
date: 2026-04-03
deciders: [Tseren]
context: "WP-187 Ф1 — спецификация BYOB для Knowledge Gateway"
related:
  pack: [DP.D.036, DP.D.037, DP.IWE.003]
  uses: [ADR-IWE-001]
  realized_by: [WP-187]
family: F6
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-003: Gateway Backend Interface — контракт MCP-серверов за Gateway

## 1. Контекст

Gateway (`mcp.aisystant.com`) агрегирует три MCP-сервера: knowledge-mcp (L2), digital-twin-mcp (L2), personal-knowledge-mcp (L4). Сегодня все три — наши сервисы с жёстко прописанными URL в `wrangler.toml`.

При масштабировании (T4-пользователи с собственными источниками, BYOB — DP.D.036) Gateway должен подключать новые backend-серверы **без изменения кода Gateway**. Нужен формальный контракт: что Gateway ожидает от любого backend MCP.

## 2. Решение

Определён **Gateway Backend Interface** — набор MCP-методов и поведений, которым должен соответствовать любой MCP-сервер, подключаемый к Gateway.

## 3. Gateway Backend Interface

### 3.1. Обязательные MCP-методы

Каждый backend MCP, подключаемый к Gateway, ДОЛЖЕН реализовать:

```typescript
// Минимальный контракт backend MCP для Gateway
interface GatewayBackendMcp {
  // --- MCP Protocol (обязательные) ---

  /** Инициализация — protocolVersion >= "2024-11-05" */
  "initialize"(): {
    protocolVersion: string;
    capabilities: { tools: {} };
    serverInfo: { name: string; version: string };
  };

  /** Список инструментов — Gateway добавляет namespace-префикс */
  "tools/list"(): {
    tools: ToolDefinition[];
  };

  /** Вызов инструмента */
  "tools/call"(params: { name: string; arguments: Record<string, unknown> }): {
    content: ContentBlock[];
  };

  /** Пинг — healthcheck */
  "ping"(): {};
}
```

### 3.2. Обязательный инструмент: `search`

Каждый backend, участвующий в unified search (fan-out), ДОЛЖЕН реализовать инструмент `search`:

```typescript
interface SearchTool {
  name: "search";
  inputSchema: {
    query: string;       // Текст запроса (обязательный)
    limit?: number;      // Макс. результатов (по умолч. 5)
    source?: string;     // Фильтр по источнику
    source_type?: string; // Фильтр по типу источника
  };
  output: SearchResult[];
}

interface SearchResult {
  filename: string;       // Уникальный идентификатор документа в рамках source
  source: string;         // Имя источника (например, "PACK-digital-platform")
  score: number;          // Релевантность [0.0, 1.0] — нормализованный
  content_preview: string; // Первые ~500 символов совпадения
  github_url?: string;    // Опциональная ссылка на GitHub
  source_type?: string;   // Тип источника (pack, ds, content, fmt)
}
```

**Контракт score:** Gateway выполняет merge результатов из разных backend по `score`. Все backend ДОЛЖНЫ возвращать score в нормализованном диапазоне [0.0, 1.0], где:
- 1.0 = точное совпадение
- 0.0 = нет совпадения
- Текущие реализации: cosine similarity (pgvector) уже в [0, 1]

**Дедупликация:** Gateway дедуплицирует по ключу `source:filename`. При совпадении — берёт результат с большим score.

### 3.3. Опциональные инструменты

| Инструмент | Назначение | Кто реализует сейчас |
|------------|-----------|---------------------|
| `get_document(filename, source?)` | Получить полный текст документа | knowledge-mcp, personal-knowledge-mcp |
| `list_sources(source_type?)` | Список проиндексированных источников | knowledge-mcp, personal-knowledge-mcp |
| `get_tailor_context(user_id)` | Контекст ЦД пользователя | digital-twin-mcp |
| `propose_capture(content, location, user_id)` | Предложение записи в репо пользователя | personal-knowledge-mcp |
| `write(path, content, user_id)` | Запись в репо через GitHub App | personal-knowledge-mcp |
| `knowledge_feedback(document_id, query, helpfulness, user_id)` | Обратная связь по релевантности | knowledge-mcp (WP-184) |

Опциональные инструменты Gateway не проверяет — они проксируются напрямую через namespace-роутинг (`toolPrefix_toolName`).

### 3.4. Требования к HTTP-транспорту

| Свойство | Требование |
|----------|-----------|
| Endpoint | `POST /mcp` — MCP JSON-RPC 2.0 |
| Content-Type | `application/json` |
| Healthcheck | `GET /health` → 200 OK |
| Latency | p95 < 500ms для `search`, p95 < 200ms для `ping` |
| Concurrency | Должен выдерживать ≥10 concurrent fan-out запросов |
| Errors | MCP JSON-RPC error codes (-32000...-32099 для backend-специфичных) |

### 3.5. Требования к изоляции (RLS)

Если backend хранит данные нескольких пользователей:

1. `user_id` ДОЛЖЕН извлекаться из JWT (Ory session), НЕ из параметра запроса
2. WHERE-фильтр по `user_id` ДОЛЖЕН применяться ко ВСЕМ запросам чтения
3. Отсутствие `user_id` → доступ только к публичным данным (knowledge-mcp L2)

**Исключение:** knowledge-mcp (L2 Platform) содержит только публичное знание — RLS не требуется.

## 4. Три текущие реализации

### 4.1. knowledge-mcp (L2 Platform)

| Свойство | Значение |
|----------|---------|
| URL | `knowledge-mcp.aisystant.workers.dev` |
| toolPrefix | `knowledge` |
| Хранилище | Neon pgvector (1024d, text-embedding-3-small) |
| Поиск | Гибридный: keyword (pg_trgm + tsvector) → vector (cosine) → fallback merge |
| RLS | Нет (публичное знание) |
| Источники | 16 платформенных (ZP, FPF, SPF, Pack-*, courses, guides) |

### 4.2. personal-knowledge-mcp (L4 Personal)

| Свойство | Значение |
|----------|---------|
| URL | `personal-knowledge-mcp.aisystant.workers.dev` |
| toolPrefix | `personal` |
| Хранилище | Neon pgvector (shared DB, RLS по user_id — ADR-IWE-001) |
| Поиск | Гибридный (идентичен knowledge-mcp) |
| RLS | `WHERE user_id = $1` (из JWT) |
| Источники | Репо пользователя (выбранные явно) |
| Доп. инструменты | `propose_capture`, `write` (GitHub App) |

### 4.3. digital-twin-mcp (L2 Platform, per-user)

| Свойство | Значение |
|----------|---------|
| URL | `digital-twin-mcp.aisystant.workers.dev` |
| toolPrefix | `dt` |
| Хранилище | Neon (реляционное, не pgvector) |
| RLS | `WHERE user_id = $1` (из JWT) |
| Особенность | Read-only потребитель `3_derived`. Writer = R28 Профилировщик |
| Не участвует | В unified search (fan-out) — нет инструмента `search` |

## 5. Knowledge Gate (валидация нового backend)

При подключении нового backend к Gateway выполняется Knowledge Gate — проверка соответствия контракту.

### 5.1. Автоматические проверки (compliance check)

```
KG-01: POST /mcp initialize → protocolVersion >= "2024-11-05"
KG-02: POST /mcp tools/list → массив tools, каждый имеет name + inputSchema
KG-03: POST /mcp tools/call search → возвращает SearchResult[] с score в [0, 1]
KG-04: GET /health → 200 в < 1s
KG-05: POST /mcp ping → ответ в < 200ms
KG-06: search(query="test") → content_preview не пуст, filename не пуст
KG-07: Дедупликация: два результата с одним filename+source → Gateway берёт max score
```

### 5.2. Ручные проверки (при первом подключении)

```
KG-10: Источники не дублируют L2 Platform (нет ZP/FPF/SPF в пользовательском backend)
KG-11: Score калиброван: top-1 результат по известному запросу ≥ 0.7
KG-12: Latency p95 < 500ms при 5 concurrent запросах
KG-13: При наличии user_id — RLS тест: user A не видит данные user B
```

### 5.3. Результат Knowledge Gate

| Результат | Действие |
|-----------|---------|
| ✅ Все KG-01..KG-07 пройдены | Backend подключается к Gateway |
| ⚠️ KG-06/KG-07 failed | Backend подключается, но не участвует в fan-out search |
| ❌ KG-01..KG-05 failed | Backend НЕ подключается — нарушен контракт |

## 6. Pipeline подключения нового backend

### 6.1. Для платформенного MCP (наш сервис)

```
1. Реализовать GatewayBackendMcp interface
2. Деплой на Cloudflare Workers
3. Knowledge Gate (автоматический) → KG-01..KG-07
4. Добавить URL в wrangler.toml Gateway (secret)
5. Добавить в getBackends() — name, url, toolPrefix
6. Деплой Gateway
```

### 6.2. Для пользовательского MCP (T4, BYOB)

> Статус: спецификация. Реализация — WP-187 Ф2.

```
1. Пользователь деплоит свой MCP (форк шаблона или свой код)
2. Указывает URL в настройках Gateway (UI / .exocortex.env)
3. Gateway вызывает Knowledge Gate (KG-01..KG-07) автоматически
4. При успехе: backend добавляется в fan-out для данного user_id
5. При неуспехе: ошибка с указанием провалившегося KG-шага
```

**Backend Registry (будущее):**

```typescript
// Gateway хранит список подключённых backend per user
interface BackendRegistration {
  userId: string;         // Ory user_id
  backendUrl: string;     // URL MCP-сервера
  toolPrefix: string;     // Namespace (уникальный для пользователя)
  name: string;           // Человекочитаемое имя
  status: "active" | "failed" | "pending_validation";
  lastHealthCheck: string; // ISO datetime
  knowledgeGateResult: "passed" | "partial" | "failed";
}
```

**Хранение:** Neon, таблица `backend_registry`, RLS по `user_id`.

## 7. Шаблон для нового backend MCP

> Шаблон будет создан в DS-MCP/ при реализации Ф2. Основа — personal-knowledge-mcp.

Минимальный backend MCP = Cloudflare Worker с:
- `initialize`, `tools/list`, `tools/call`, `ping`
- `search` tool (обязательный для fan-out)
- Neon pgvector или Supabase pgvector или SQLite + vec0

## 8. Связь с архитектурными решениями

| Решение | Связь |
|---------|-------|
| DP.D.036 (BYOB) | Этот ADR формализует контракт, упомянутый в §4 DP.D.036 |
| DP.D.037 (три категории MCP) | Backend Interface — контракт для платформенных MCP. Пользовательские — через Knowledge Gate |
| ADR-IWE-001 (embeddings isolation) | RLS-требование §3.5 реализовано через ADR-IWE-001 |
| MCP-NAMESPACE.md | Namespace-роутинг §3.3 — через toolPrefix из namespace-соглашения |
| Gateway index.ts | `getBackends()`, `routeToolCall()`, `fanOutSearch()` — текущая реализация контракта |

## 9. Последствия

**Положительные:**
- Новые backend подключаются без изменения кода Gateway (только конфигурация)
- Knowledge Gate предотвращает подключение несовместимых серверов
- Score-нормализация обеспечивает корректный merge в fan-out

**Отрицательные:**
- Все backend должны реализовать MCP JSON-RPC — нет REST-адаптера
- Score-нормализация между разными embedding-моделями не гарантирована (mitigation: KG-11 калибровка)

**Риски:**
- Backend с нестандартным score-диапазоном может доминировать/проигрывать в fan-out. Митигация: Knowledge Gate KG-11
- Пользовательский backend может быть медленным → таймаут fan-out. Митигация: Gateway ставит deadline 3s на каждый backend в `Promise.allSettled`
