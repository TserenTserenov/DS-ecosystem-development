---
id: ADR-IWE-007
title: "Content Integrity при индексации Knowledge MCP"
status: proposed
date: 2026-04-06
deciders: [Tseren]
context: "WP-73 Phase 2 — защита knowledge-mcp от prompt injection и stale content"
related:
  pack: [DP.ARCH.003, DP.D.036]
  uses: [ADR-IWE-003, ADR-IWE-004]
  realized_by: [WP-187]
family: F6
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-007: Content Integrity при индексации Knowledge MCP

## 1. Контекст

Knowledge-mcp индексирует markdown-контент из Pack и DS репозиториев (~5400 документов, 9 источников). Контент превращается в embeddings и доступен через search API. LLM использует результаты поиска как контекст для ответов.

**Угрозы:**
1. **Prompt injection через контент** — злонамеренный или случайный текст в индексируемом документе, который манипулирует поведением LLM при поиске
2. **Stale content** — устаревший документ в индексе, который противоречит актуальному состоянию репо
3. **Unauthorized content** — документ, не прошедший review, попавший в индекс (черновик, experiment branch)

**Текущее состояние:**
- Content hash (SHA-256, первые 16 символов) используется для delta-detection при переиндексации
- Parameterized SQL queries (нет SQL injection)
- Нет верификации аутентичности контента (Git commit signature)
- Нет staleness detection (сравнение даты индексации vs последний commit)
- CLAUDE.md файлы **не индексируются** (и не должны — это repo metadata, не domain knowledge)

## 2. Решение

### 2.1. CLAUDE.md — НЕ индексировать

CLAUDE.md = инструкции для агента, не доменное знание. Индексация создаёт вектор атаки (системные инструкции доступны через search). **Явный запрет:** CLAUDE.md, `.claude/`, `memory/` — в exclusion list инжестора.

### 2.2. Content hash pinning при деплое

При каждом деплое knowledge-mcp:

```
1. git pull всех source-репозиториев
2. Для каждого source: вычислить manifest = {filepath: SHA-256(content)}
3. Сравнить с предыдущим manifest (хранится в Neon, таблица `indexing.manifests`)
4. Переиндексировать только изменённые файлы
5. Записать новый manifest + git commit SHA + timestamp
```

**Таблица:**

```sql
CREATE TABLE indexing.manifests (
  source       TEXT NOT NULL,        -- 'pack-digital-platform', 'ds-ecosystem' и т.д.
  filepath     TEXT NOT NULL,        -- относительный путь в репо
  content_hash TEXT NOT NULL,        -- SHA-256 полного содержимого
  git_commit   TEXT NOT NULL,        -- commit SHA на момент индексации
  indexed_at   TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (source, filepath)
);
```

### 2.3. Exclusion patterns

```yaml
# sources.json — новое поле exclude_patterns
exclude_patterns:
  - "CLAUDE.md"
  - ".claude/**"
  - "memory/**"
  - "node_modules/**"
  - "*.env*"
  - ".git/**"
  - "**/*.secret*"
```

### 2.4. Staleness detection

Cron-задача (ежедневно или при deploy):

```
1. Для каждого source: git log --since=<last_indexed_at> --name-only
2. Если есть изменённые файлы, не отражённые в manifests → пометить stale
3. Если stale > 7 дней → alert в Activity Hub (event_type: system_alert)
```

### 2.5. Content validation (lightweight)

Перед индексацией каждого документа:

| Проверка | Действие при нарушении |
|----------|----------------------|
| Размер > 100KB | Skip + warning в лог |
| Содержит `<script>`, `javascript:`, `data:text/html` | Skip + alert |
| Содержит паттерны prompt injection (`ignore previous`, `system:`, `you are now`) | Flag для review, индексировать с `confidence: 0.5` |
| YAML frontmatter невалидный | Skip + warning |

### 2.6. Audit trail

Все операции индексации записываются в `indexing.audit_log`:

```sql
CREATE TABLE indexing.audit_log (
  id           BIGSERIAL PRIMARY KEY,
  source       TEXT NOT NULL,
  operation    TEXT NOT NULL,  -- 'indexed', 'skipped', 'flagged', 'deleted'
  filepath     TEXT NOT NULL,
  content_hash TEXT,
  reason       TEXT,           -- 'new', 'changed', 'stale', 'too_large', 'injection_pattern'
  created_at   TIMESTAMPTZ DEFAULT now()
);
```

## 3. Фазы внедрения

| Фаза | Что | Когда |
|------|-----|-------|
| **A** | Exclusion patterns (CLAUDE.md, .claude/, memory/) | Сейчас (1h) |
| **B** | Manifest table + hash pinning при деплое | С WP-187 Ф3 |
| **C** | Content validation (size, injection patterns) | С Knowledge Gateway BYOB |
| **D** | Staleness detection + alerts | С Activity Hub Ф5 |

## 4. Последствия

**Плюсы:**
- Защита от prompt injection через индексированный контент
- Аудируемость: кто, когда, что проиндексировал
- Staleness detection предотвращает противоречия между индексом и реальностью
- Exclusion list предотвращает утечку системных инструкций

**Минусы:**
- Дополнительная таблица в Neon (+незначительный overhead)
- Content validation может дать false positive на легитимных документах (напр. документ, описывающий prompt injection как тему)

**Риски:**
- Regex-паттерны injection detection — гонка вооружений. Не полагаться только на них; основная защита — exclusion list + manifest integrity
