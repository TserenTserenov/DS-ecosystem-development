---
id: ADR-IWE-004
title: "GitHub App Installation Token для записи в репо пользователя"
status: accepted
date: 2026-04-03
deciders: [Tseren]
context: "WP-187 Ф2 — personal-knowledge-mcp нужен write-доступ к GitHub-репо пользователя"
related:
  pack: [DP.D.036, DP.D.037]
  uses: [ADR-IWE-001, ADR-IWE-003]
  realized_by: [WP-187]
family: F6
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-004: GitHub App Installation Token для записи в репо пользователя

## 1. Контекст

Personal-knowledge-mcp (L4) должен уметь писать в GitHub-репо пользователя:
- `propose_capture(content, location)` — предложение записи (с подтверждением или автоматически)
- `write(path, content)` — прямая запись в файл

**Проблема:** какой механизм авторизации использовать для доступа к репо пользователя?

**Ограничения:**
- Пользователь не должен передавать Personal Access Token (PAT) — это full-account scope, нарушает принцип минимальных привилегий
- OAuth через бота (CLAUDE.md §9) — платформа не должна хранить долгоживущие токены с широким доступом
- Запись только в явно разрешённые репо (DP.D.037 §4: «пользователь явно выбирает»)

## 2. Рассмотренные варианты

| Вариант | Scope | Хранение токена | Риск |
|---------|-------|----------------|------|
| A. **GitHub App** | Per-repo (installation) | Генерируется на лету (1h TTL) | Минимальный |
| B. Fine-grained PAT | Per-repo | Хранится у нас (encrypted) | Утечка = доступ пока не отзовут |
| C. OAuth App (classic) | Full account | Refresh token у нас | Широкий scope |
| D. GitHub Actions (dispatch) | Per-repo | GITHUB_TOKEN в Actions | Привязка к CI, не к MCP |

## 3. Решение

**Принят вариант A — GitHub App Installation Token.**

### 3.1. Как работает

```
1. Мы регистрируем GitHub App "Aisystant Knowledge" (один раз)
   Permissions: contents:write, metadata:read — ТОЛЬКО эти
   
2. Пользователь «устанавливает» App на свои репо
   GitHub UI: Settings → Applications → Install → выбрать репо
   Результат: installation_id привязан к конкретным репо
   
3. При каждой записи personal-knowledge-mcp:
   a. JWT из App private key (exp: 10 min)
   b. POST /app/installations/{id}/access_tokens → Installation Token (1h TTL)
   c. Используем Installation Token для Git operations
   d. Токен истекает — не нужно хранить
```

### 3.2. Почему GitHub App

1. **Минимальный scope:** `contents:write` только на выбранные репо (не весь аккаунт)
2. **Короткоживущий токен:** 1h TTL, генерируется на лету — нечего утечь
3. **Пользовательский контроль:** пользователь в любой момент отзывает установку через GitHub UI
4. **Стандартный паттерн:** GitHub рекомендует для server-to-server (не interactive)
5. **Audit trail:** все коммиты подписаны App identity → видно что писала платформа

### 3.3. Что хранить на платформе

| Секрет | Где | Кто знает |
|--------|-----|-----------|
| App ID | `wrangler.toml` (не секрет) | Публичный |
| App Private Key | `wrangler secret` | Только Worker |
| Installation ID per user | Neon, таблица `github_installations` | Per-user (RLS) |

```sql
CREATE TABLE github_installations (
  user_id TEXT NOT NULL,           -- Ory user_id
  installation_id BIGINT NOT NULL, -- GitHub App installation
  repos TEXT[] NOT NULL,           -- Разрешённые репо ['owner/repo1', 'owner/repo2']
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id)
);
```

### 3.4. Поток подключения (onboarding)

```
1. Пользователь нажимает «Подключить знания» в UI (или /connect в боте)
2. Редирект → github.com/apps/aisystant-knowledge/installations/new
3. Пользователь выбирает репо → Install
4. GitHub POST webhook → installation.created event
5. Платформа сохраняет installation_id + repos в Neon
6. Запускает индексацию выбранных репо (personal-knowledge-mcp ingest)
7. Пользователь видит «Знания подключены. N документов проиндексировано.»
```

### 3.5. Поток записи (runtime)

```
1. AI-агент вызывает personal_write(path, content) через Gateway
2. Gateway проверяет Ory token → user_id
3. personal-knowledge-mcp:
   a. Достаёт installation_id из Neon по user_id
   b. Проверяет что целевой repo в разрешённом списке repos[]
   c. Генерирует Installation Token (App JWT → POST /installations/{id}/access_tokens)
   d. PUT /repos/{owner}/{repo}/contents/{path} через Installation Token
   e. Ставит в очередь переиндексацию изменённого файла
   f. Публикует ingest_event в Activity Hub (side effect)
4. Ответ клиенту: { sha, commit_url, indexed: true }
```

### 3.6. Поток переиндексации (webhook)

```
1. Push в подключённый репо (пользователь или платформа)
2. GitHub POST webhook → push event с list of changed files
3. personal-knowledge-mcp:
   a. Проверяет installation_id → user_id
   b. Переиндексирует только изменённые файлы (delta ingest)
   c. Обновляет embeddings в Neon с user_id (RLS)
```

## 4. GitHub App конфигурация

```yaml
# Параметры регистрации GitHub App
name: "Aisystant Knowledge"
description: "Подключение ваших знаний к IWE Knowledge Gateway"
url: "https://system-school.ru/knowledge"
callback_url: "https://mcp.aisystant.com/github/callback"
setup_url: "https://mcp.aisystant.com/github/setup"
webhook_url: "https://mcp.aisystant.com/github/webhook"
webhook_secret: <secret>

# Permissions (минимальные)
permissions:
  contents: write      # Чтение и запись файлов
  metadata: read       # Чтение метаданных репо

# Subscribe to events
events:
  - push               # Для переиндексации при изменениях
  - installation        # Для onboarding/offboarding

# Visibility
public: true           # Любой пользователь может установить
```

## 5. Безопасность

| Риск | Митигация |
|------|----------|
| App Private Key утечёт | Хранится только в Cloudflare Secrets (encrypted at rest). Ротация: генерируем новый через GitHub UI |
| Пользователь отзовёт установку | Webhook `installation.deleted` → удаляем installation_id + embeddings |
| Запись не в тот репо | Проверка repos[] перед каждой записью. Installation Token и так scoped на разрешённые репо |
| Rate limiting | GitHub App: 5000 req/h per installation. При ~10 writes/day — запас 500x |
| Вредоносный контент от AI | propose_capture (default mode) показывает diff пользователю перед записью |

## 6. Связь с архитектурой

| Решение | Связь |
|---------|-------|
| ADR-IWE-003 (Backend Interface) | Write tools — часть контракта personal-knowledge-mcp |
| ADR-IWE-001 (embeddings isolation) | Переиндексация пишет embeddings с user_id (RLS) |
| DP.D.036 (BYOB) | GitHub App = механизм авторизации BYOB write-path |
| DP.D.037 (три категории MCP) | personal-knowledge-mcp = платформенный сервис, GitHub App = делегированный доступ |
| MCP-NAMESPACE.md | write + propose_capture tools специфицированы здесь |

## 7. Последствия

**Положительные:**
- Минимальный scope (только contents:write на выбранные репо)
- Нет долгоживущих токенов (1h TTL, генерируется на лету)
- Пользовательский контроль через GitHub UI (install/uninstall)
- Audit trail: коммиты подписаны App identity

**Отрицательные:**
- Нужно зарегистрировать GitHub App (одноразово)
- Webhook endpoint в Gateway для installation/push events
- Дополнительная таблица `github_installations` в Neon

**Следующие шаги:**
1. Зарегистрировать GitHub App «Aisystant Knowledge» в org aisystant
2. Добавить `GITHUB_APP_ID` и `GITHUB_APP_PRIVATE_KEY` в wrangler secrets
3. Реализовать webhook handler в Gateway (`/github/webhook`)
4. Реализовать `write` и `propose_capture` в personal-knowledge-mcp
5. Реализовать delta ingest (переиндексация по push webhook)
