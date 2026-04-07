---
id: ADR-IWE-008
title: "Identity: ory_id как единственный универсальный идентификатор"
status: accepted
date: 2026-04-07
deciders: [Tseren, Андрей]
context: "WP-73 встреча 4 — Identity Hub, DE-34, привязка ory_id ↔ lms_user_id"
related:
  pack: [DP.ARCH.001, DP.D.034]
  uses: [ADR-006, ADR-014]
  realized_by: [WP-73, WP-183, WP-109]
family: F6
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-008: Identity — ory_id как единственный универсальный идентификатор

## 1. Контекст

Платформа Aisystant исторически использует несколько идентификаторов пользователя:

| Система | Идентификатор | Тип |
|---------|---------------|-----|
| LMS Aisystant | `lms_user_id` (autoincrement) | Внутренний PK |
| Telegram-бот | `telegram_id` | Внешний (Telegram API) |
| Ory Network | `ory_id` (UUID) | Внешний (Ory Identity) |
| Email | email | Внешний |

**Проблема:** при интеграции Ory (ADR-006) возник вопрос — как связать существующих пользователей? Два варианта:

- **(A) Добавить `lms_user_id` в Ory traits** — Ory знает про LMS. Каждый сервис получает `lms_user_id` из Ory-токена
- **(B) Использовать только `ory_id`** — Ory не знает про LMS. Если сервису нужен `lms_user_id`, он запрашивает его через LMS API по Ory-токену

Вариант (A) создаёт coupling: Ory traits становятся реестром маппингов для всех систем. При появлении новой системы — нужно добавлять новый trait. Traits раздуваются.

## 2. Решение

**Вариант (B): `ory_id` = единственный универсальный идентификатор.**

### 2.1. Принципы

1. **НЕ добавлять `lms_user_id` в Ory traits.** Ory хранит только свои данные (email, имя, статус верификации)
2. **Каждый сервис создаёт локальную учётку при первом входе пользователя с `ory_id`.** Lazy provisioning, не массовая миграция
3. **Если сервису нужен `lms_user_id`** — запрашивать через LMS API по Ory-токену. Адаптеры: [bonuses](https://github.com/aisystant/bonuses) (`aisistant_client`), [posthog-api](https://github.com/aisystant/posthog-api)
4. **Звезда, не mesh:** каждая система знает только свою связку с Ory (`system_local_id ↔ ory_id`). Системы не связаны между собой напрямую

### 2.2. Архитектура связей

```
                         Ory (ory_id)
                              |
              +---------------+---------------+
              |               |               |
         Бот Aist        LMS Aisystant     ЦД (Neon)
         telegram_id     lms_user_id       ory_id (PK)
         ↔ ory_id        ↔ ory_id          
         (crm.identity   (LMS API          (прямая
          _links)         по Ory-токену)    идентификация)
```

**Звезда через Ory (O(n) связей)** вместо mesh (O(n^2) интеграций).

### 2.3. Lazy provisioning

При первом входе пользователя в систему:

```
1. Пользователь авторизуется через Ory → получает JWT с ory_id
2. Сервис получает ory_id из JWT
3. SELECT * FROM users WHERE ory_id = ?
4. Если нет → INSERT (ory_id, created_at)
5. Если нужны данные из LMS → GET /api/user?ory_token=... → lms_user_id, email, name
6. Сохранить маппинг локально
```

**Не массовая миграция.** Учётки создаются по мере обращения пользователей.

### 2.4. Identity linking (CRM)

Таблица `crm.identity_links` связывает `telegram_id ↔ ory_id`:

- **Автоматически:** Ory webhook `identity.created` → бот проверяет наличие `telegram_id` в `crm.leads` → если есть, создаёт link
- **Вручную:** пользователь вызывает `/link` в боте
- **Cron (ежедневно):** найти записи без match → уведомить менеджера

### 2.5. Мягкое удаление

Пользовательские данные не удаляются физически. Флаг `archived_at` (TIMESTAMP, NULL = активный). Git-история сохраняется.

## 3. Альтернативы (отклонены)

| Вариант | Почему отклонён |
|---------|-----------------|
| `lms_user_id` в Ory traits | Coupling: Ory traits = реестр маппингов для всех систем. Раздувание traits при каждой новой системе |
| Массовая миграция ID | Downtime, ошибки маппинга, сложность отката. Lazy provisioning безопаснее |
| Промежуточный маппинг-сервис | Лишний SPOF. Звезда через Ory проще и надёжнее |

## 4. Последствия

**Положительные:**
- Единый ID для всех новых систем (CRM, Billing, ЦД, Knowledge Gateway)
- Нет coupling между Ory и legacy LMS
- Lazy provisioning = нулевой downtime при миграции
- Звезда = O(n) интеграций вместо O(n^2)

**Отрицательные:**
- Первый запрос пользователя в новую систему чуть медленнее (provisioning)
- LMS API должен уметь отвечать по Ory-токену (доработка Димы)

## 5. Связанные данные (ЦД ↔ LMS)

**Решение:** данные из LMS подтягиваются при первом входе пользователя в ЦД (не массовая миграция). Код адаптеров: `bonuses` (`aisistant_client`), `posthog-api`.

## 6. Реализация

| Система | Что сделать | Кто | Приоритет |
|---------|-------------|-----|-----------|
| Бот Aist | `crm.identity_links` (telegram_id ↔ ory_id). Lazy provisioning при `/start` | Tseren | Высокий |
| ЦД (Neon) | `public.users` с `ory_id` PK. Подтянуть данные из LMS при первом входе | Tseren | Высокий |
| LMS Aisystant | API endpoint: GET user by Ory-токен → lms_user_id | Дима | Высокий |
| Payment Registry | `ory_id` в записи оплат. До Ory — fallback на telegram_id/email | Tseren + Дима | Средний |
| Knowledge Gateway | Уже использует ory_id (OAuth2 PKCE) | — | Done |
| Directus | Introspects Neon. RBAC по ory_id | Tseren | Средний |

---

*Принято: 7 апреля 2026, встреча 4 с архитектором.*
