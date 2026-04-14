---
id: ADR-IWE-012
title: "Независимая JWT-верификация в каждом приватном MCP + проверка подписки на Gateway"
status: accepted
date: 2026-04-14
updated: 2026-04-14
deciders: [Андрей, Tseren]
family: F8
kernel: C
system: C2
role: Architecture
related:
  - DP.D.031
  - DP.SC.112
  - WP-212
  - ADR-IWE-008
---

# ADR-IWE-012: Независимая JWT-верификация в каждом приватном MCP + проверка подписки на Gateway

## Контекст

Gateway — единая точка входа, которая проверяет подписку и роутит запросы к MCP-серверам. До этого решения каждый MCP доверял заголовку `X-User-Id` от Gateway на слово.

**Проблема:** MCP-серверы (Cloudflare Workers) имеют публичные URL. Любой знает URL → может обратиться напрямую, минуя Gateway, с произвольным `X-User-Id`.

Инцидент: personal-knowledge-mcp возвращал личные документы любому кто знал `ory_id` пользователя и передавал его в заголовке.

**Вторая проблема (обнаружена 14 апр):** дублирование проверки подписки. Gateway проверял подписку через `subscription_grants` (DB #1 — platform), backends — через ту же таблицу, но с другим DATABASE_URL (DB #2 — старая aist_bot). Рассинхронизация баз → 401/403 у всех пользователей.

## Решение (текущее — Вариант B, с 14 апр)

**Два независимых слоя:**

1. **JWT-верификация** — каждый приватный MCP верифицирует подпись токена самостоятельно через Ory JWKS (jose + `/.well-known/jwks.json`). Не доверяет заголовкам.
2. **Проверка подписки** — **только Gateway**. Backends доверяют Gateway: если запрос дошёл с валидным JWT — подписка уже проверена.

```typescript
// Паттерн для всех приватных MCP (Вариант B)
const token = authHeader.slice(7);
const userId = await verifyJwtLocally(env.ORY_URL, token); // JWT ✅ независимо
if (!userId) return 401;

// Подписка НЕ проверяется здесь — Gateway гарантирует это до проксирования
const result = await handleRequest(userId);
```

```typescript
// Gateway (единственное место проверки подписки)
const auth = await validateOryToken(env, token); // JWT + subscription_grants
if (!auth.hasSubscription) return 403;
// → proxy to backends
```

## Целевое решение (Вариант E — требует Пашу)

Добавить claim `has_subscription: true/false` в JWT через Hydra token hook. Тогда:
- Gateway читает claim из токена — 0 DB запросов
- Backends читают тот же claim — 0 DB запросов
- `subscription_grants` перестаёт быть узким местом

АрхГейт пройден (14 апр): Вариант E = ✅ по скорости, ⚠️ по безопасности (окно TTL ~20 мин после отмены подписки — принято как допустимый риск).

## Доступность по типу MCP

| MCP | Без подписки | С подпиской |
|-----|-------------|-------------|
| knowledge-mcp (публичный) | ✅ JWT достаточно | ✅ |
| dt-mcp (закрытый) | ❌ 403 на Gateway | ✅ |
| personal-mcp (закрытый) | ❌ 403 на Gateway | ✅ |

## Рассмотренные альтернативы

| Вариант | Статус | Причина |
|---------|--------|---------|
| Доверять X-User-Id от Gateway | ❌ Отклонён | Уязвимость при прямом обращении к MCP |
| Двойная проверка (A) | ❌ Отклонён | Рассинхронизация DATABASE_URL → 401 |
| Только Gateway (C) | ❌ Отклонён | Дыра прямого доступа без network isolation |
| Gateway + X-header (D) | ⚠️ Отклонён | Ory coupling отсутствует, но уступает E по скорости |
| JWT claim (E) | ✅ Цель | 0 DB запросов, требует Hydra token hook у Паши |

## Последствия

- **knowledge-mcp**: публичный — JWT без проверки подписки ✅
- **personal-knowledge-mcp**: Вариант B реализован 14 апр
- **digital-twin-mcp**: Вариант B реализован 14 апр
- Все новые приватные MCP: только JWT-верификация, без DB-проверки подписки
