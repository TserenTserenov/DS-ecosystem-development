---
id: ADR-IWE-012
title: "Независимая JWT-верификация в каждом приватном MCP"
status: accepted
date: 2026-04-14
deciders: [Андрей, Tseren]
family: F8
kernel: C
system: C2
role: Architecture
related:
  - DP.D.031
  - WP-212
  - ADR-IWE-008
---

# ADR-IWE-012: Независимая JWT-верификация в каждом приватном MCP

## Контекст

Gateway — единая точка входа, которая проверяет подписку и роутит запросы к MCP-серверам. До этого решения каждый MCP доверял заголовку `X-User-Id` от Gateway на слово.

**Проблема:** MCP-серверы (Cloudflare Workers) имеют публичные URL. Любой знает URL → может обратиться напрямую, минуя Gateway, с произвольным `X-User-Id`.

Инцидент: personal-knowledge-mcp возвращал личные документы любому кто знал `ory_id` пользователя и передавал его в заголовке.

## Решение

**Принцип Андрея:** каждый приватный MCP верифицирует JWT-токен самостоятельно через Ory JWKS.

Gateway остаётся роутером (объединяет MCP в один endpoint + проверяет подписку). Но верификация криптографической подписи токена — в каждом MCP независимо.

## Паттерн (одинаковый для всех приватных MCP)

```typescript
// 1. Верификация подписи
const authHeader = request.headers.get("Authorization");
if (authHeader?.startsWith("Bearer ") && env.ORY_URL) {
  userId = await verifyJwtLocally(env.ORY_URL, token); // jose + JWKS
} else if (!authHeader) {
  return 401; // нет токена — нет доступа
}
if (!userId) return 401; // невалидный JWT

// 2. Проверка подписки
const hasSub = await checkSubscription(env.DATABASE_URL, userId);
if (!hasSub) return 403;
```

## Рассмотренные альтернативы

| Вариант | Отклонён потому что |
|---------|-------------------|
| Доверять X-User-Id от Gateway | Уязвимость при прямом обращении к MCP |
| Только Gateway проверяет всё | Defense-in-depth нарушен |
| Отдельный auth-сервис | Лишняя сложность, latency |

## Последствия

- **knowledge-mcp**: особый случай — публичный, верификация без требования подписки
- **personal-knowledge-mcp**: реализовано 13-14 апр (B4.21 WP-212)
- **digital-twin-mcp**: требует рефакторинга — сейчас свой OAuth2 AS, нужно перейти на JWKS (WP-222)
- Все новые приватные MCP создаются с этим паттерном сразу
