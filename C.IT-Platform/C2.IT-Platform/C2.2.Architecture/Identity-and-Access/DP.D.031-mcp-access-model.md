---
id: DP.D.031
name: "MCP Access Model: публичный vs приватный + принцип независимой верификации"
type: distinction
status: active
created: 2026-02-19
updated: 2026-04-14
trust:
  F: 4
  G: domain
  R: 0.9
related:
  extends: [DP.ARCH.002, DP.D.024]
  uses: [DP.EXOCORTEX.001, DP.IWE.003]
  adr: ADR-012-mcp-independent-jwt-verification
---

# MCP Access Model: публичный vs приватный + принцип независимой верификации

## 1. Различение: публичный vs приватный MCP

| MCP-сервер | Тип доступа | Что хранит | Требует подписки |
|------------|------------|------------|-----------------|
| **knowledge-mcp** | **Публичный** (особый случай) | Pack-сущности, онтология, 5400+ docs | ❌ нет — платформенные знания открыты всем |
| **guides-mcp** | **Публичный** | Руководства Aisystant | ❌ нет |
| **personal-knowledge-mcp** | **Приватный** | Личные репо и заметки пользователя | ✅ да |
| **digital-twin-mcp** | **Приватный** | Цифровой двойник, персональные данные | ✅ да |
| **gateway-mcp** | **Роутер** | — | ✅ да (первый барьер) |

**Критерий:** знания домена (Pack, онтология) — публичны по природе. Персональные данные пользователя — изолированы.

## 2. Принцип независимой верификации (идея Андрея, 2026-04-14)

> **Каждый приватный MCP верифицирует токен сам, независимо от Gateway.**

Gateway — роутер (объединяет MCP в один endpoint). НЕ единственная точка доверия.

**Мотивация:** если Gateway взломан или обойдён (прямой URL Workers), каждый MCP всё равно не пустит без валидного JWT.

### Целевая модель безопасности

| | **gateway-mcp** | **knowledge-mcp** | **personal-knowledge-mcp** | **digital-twin-mcp** |
|--|--|--|--|--|
| **Верификация токена** | ✅ JWKS локально → fallback /userinfo | ✅ JWKS → fallback X-User-Id (внутр.) | ✅ JWKS → fallback X-User-Id (внутр.) | ✅ JWKS локально |
| **Проверка подписки** | ✅ subscription_grants | ❌ не нужно (публичный) | ✅ subscription_grants | ✅ subscription_grants |
| **Без токена → 401** | ✅ | ✅ (пускает анонимно — только публичное, это дизайн) | ✅ | ✅ |
| **Зависит от Ory** | ✅ | ✅ | ✅ | ✅ |

### Паттерн верификации (все приватные MCP)

```
1. Authorization: Bearer <token> присутствует?
   Да → verifyJwtLocally(ORY_URL, token) → sub = userId
   Нет → 401 Unauthorized

2. userId получен?
   Нет (невалидный JWT) → 401 Unauthorized

3. checkSubscription(DATABASE_URL, userId)?
   Нет → 403 Forbidden ("subscription required")
   Да → обработать запрос с userId
```

**Исключение для внутренних вызовов** (reindexer, scaffold без JWT):
- Нет Authorization → fallback на X-User-Id (только для системных вызовов без user context)
- Публичные методы (tools/list) — без auth

## 3. Реализация по статусу

| MCP | Верификация токена | Проверка подписки | 401 без токена | Статус |
|-----|-------------------|------------------|----------------|--------|
| gateway-mcp | ✅ DONE | ✅ DONE | ✅ DONE | ✅ полностью |
| knowledge-mcp | ✅ DONE (B4.21) | N/A | N/A (публичный) | ✅ особый случай |
| personal-knowledge-mcp | ✅ DONE (B4.21, 14 апр) | ❌ pending | ❌ pending | 🔄 частично |
| digital-twin-mcp | ❌ pending (переделать с KV AS) | ❌ pending | ✅ уже есть | 🔄 частично |

## 4. Источники

- Решение Андрея (устный, 2026-04-14): независимая верификация в каждом MCP
- WP-212 B4.21: реализация JWT верификации
- ADR-012: архитектурное решение по переводу digital-twin-mcp с OAuth2 AS на JWKS
