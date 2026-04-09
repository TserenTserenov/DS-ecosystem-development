---
family: F5
kernel: C
system: C2
role: Architecture
status: draft
created: 2026-04-09
target_audience:
  - "Архитектор"
  - "Backend-разработчик"
depends_on: [DP.D.031, DP.D.034, ADR-IWE-008]
related_wp: [WP-212, WP-73, WP-214, WP-215, WP-187, WP-121]
archgate: "ПРОХОДИТ (7✅/0⚠️, C+A вариант)"
---

# Концепция: Neon Authorize + Gateway Enforcement + CI Lint

> **Статус:** draft — для согласования с командой.
> После согласования формализованное знание мигрирует в PACK-digital-platform.

## Проблема

9 апреля 2026 обнаружена утечка персональных данных: personal-knowledge-mcp при отсутствии записей в `user_sources` у нового пользователя возвращал захардкоженные репозитории автора (DS-my-strategy и др.). Причина — fallback-механизм в `resolveUserContext()`.

**Системная причина:** каждый MCP-сервис (personal-knowledge-mcp, knowledge-mcp, tailor-mcp, digital-twin-mcp) самостоятельно фильтрует по `user_id`. Если разработчик забыл WHERE — данные утекают. При 5 разработчиках и растущем числе сервисов — хрупкий паттерн.

**Срочный фикс:** fallback удалён, пустой контекст вместо чужих данных (deployed 9 апр). Но нужно системное решение.

## Решение: Defense-in-Depth (3 слоя)

### Слой 1 — Neon Authorize (защита на уровне БД)

Neon Authorize — встроенная фича Neon PostgreSQL. Механизм:

1. JWT от Ory Hydra передаётся при подключении через Neon Serverless Driver
2. Neon Proxy валидирует JWT (через JWKS endpoint Ory)
3. `auth.user_id()` автоматически доступен в RLS-политиках — **без ручного SET LOCAL**

```typescript
// В каждом MCP-сервисе (Cloudflare Worker)
import { neon } from '@neondatabase/serverless';

const sql = neon(env.DATABASE_URL, {
  authToken: jwtFromOry,  // JWT access token от Ory Hydra
});

// RLS применяется автоматически — разработчик НЕ МОЖЕТ забыть
const docs = await sql`SELECT * FROM documents`;
```

```sql
-- RLS-политика (один раз на таблицу)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON documents
  USING (user_id = auth.user_id());
```

**Почему Neon Authorize, а не ручной SET LOCAL:**
- Разработчик не может забыть — контекст устанавливается proxy автоматически
- Меньше boilerplate — не нужен middleware-wrapper для транзакций
- JWT валидация на proxy — не в application code

### Слой 2 — Gateway Enforcement

Gateway-MCP блокирует запросы к private MCP-серверам **до бэкенда**, если JWT отсутствует или невалиден.

```
Ory Hydra (JWT)
      │
      ▼
┌─────────────────┐
│  Gateway-MCP     │ ← нет JWT → 403 (не доходит до бэкенда)
│  (CF Worker)     │ ← JWT есть → извлечь ory_id → передать
└────────┬────────┘
         │ X-User-Id: ory_id
         ▼
┌─────────────────┐
│  Neon (RLS)      │ ← auth.user_id() = ory_id из JWT
│  Personal MCP    │
│  Digital Twin    │
└─────────────────┘
```

### Слой 3 — CI Lint

Автоматическая проверка при каждом деплое:
- Каждая таблица с колонкой `user_id` **обязана** иметь RLS-политику
- PII-столбцы (email, phone, ФИО) **запрещены** в Neon EU (PII только в Ory)
- `FORCE ROW LEVEL SECURITY` на всех таблицах с user_id

## Blocking dependency

**Ory Hydra: JWT access tokens.** Сейчас Ory может выдавать opaque tokens. Neon Authorize требует JWT. Нужно проверить/настроить `access_token_strategy: jwt` в конфигурации Hydra.

Без этого решение **нереализуемо**. Проверка — первый шаг.

## АрхГейт (ЭМОГССБ)

Проведён 9 апреля 2026. Сравнение двух вариантов:

| Характеристика | A: RLS+GW+CI (ручной SET LOCAL) | **C+A: Neon Authorize+GW+CI** |
|----------------|:---:|:---:|
| **Э**волюционируемость | ✅ | ✅ |
| **М**асштабируемость | ✅ | ✅ |
| **О**бучаемость | ⚠️ (можно забыть SET LOCAL) | **✅** (proxy делает автоматически) |
| **Г**енеративность | ✅ | ✅ |
| **С**корость | ✅ (<2ms) | ✅ (2-5ms) |
| **С**овременность | ⚠️ (ручной middleware = 2015) | **✅** (Neon Authorize = SOTA 2024-2025) |
| **Б**езопасность | ✅ | ✅ |
| **Вердикт** | ПРОХОДИТ (2⚠️) | **ПРОХОДИТ (0⚠️)** ← рекомендуемый |

**Критичные характеристики:** Безопасность ✅, Масштабируемость ✅.
**Вето-фильтр:** ни одно правило не сработало.

### L2 (доменные расширения)

- **L2.1 Переносимость:** ⚠️ информативно — `auth.user_id()` Neon-специфичен. При миграции с Neon → fallback на ручной SET LOCAL (вариант A).
- **L2.6 Сохранность:** ✅ — SQL-миграции в git, Neon PITR backup.
- **L2.7 Интероперабельность:** ✅ — JWT = стандартный протокол.

## Исследованные и отклонённые альтернативы

| Альтернатива | Защита от "забытого WHERE" | Почему отклонена |
|-------------|:---:|---|
| **B: App middleware (Drizzle)** | 4/10 | Raw SQL обходит middleware. JOIN leak. Нет защиты на уровне БД |
| **D: DB-per-tenant** | 10/10 | Нереалистично для 10K индивидуальных пользователей на Neon. Cost, миграции ×N, cross-tenant analytics |
| **E: Cerbos WASM + RLS** | 9.5/10 | Overkill для текущей модели `user_id = owner`. Два языка политик. Ценен когда появятся роли per resource |
| **F: Ory Keto (ReBAC)** | 5/10 | Не заменяет WHERE/RLS (Keto = check, не filter). Латентность 30-150ms из CF Workers. Полезен для ролей, не для изоляции |

## Закладки на разделение RU/мир (WP-215)

Текущее решение — одна юрисдикция (Neon EU, один Ory). Закладки для безболезненного разделения:

| Закладка | Стоимость сейчас | Что даёт потом |
|----------|-----------------|----------------|
| `ory_id` как единственный ID в community-таблицах | Бесплатно (ADR-IWE-008) | При втором Ory — один ALTER TABLE для canonical_id |
| `source_region` поле в event-таблицах | 1 столбец (default 'eu') | Разделение трафика без миграции |
| PII не в Neon (а в Ory traits) | Дисциплина | При разделении Ory — PII разъезжается автоматически |
| RLS по `ory_id` (не по region) | Часть решения | Работает одинаково в 1 и 2 контурах |

**Что НЕ нужно сейчас:** identity_links, canonical_ory_id, Outbox pattern, второй Gateway, PG-RU.

## Эволюционный путь

```
Сейчас (W15-W18)              W19-W22                   Q3+
──────────────────────────────────────────────────────────────
Neon Authorize               + Keto (ReBAC)          + Cedar policies
+ Gateway + CI                 для ролей               для consent layer
(user_id = owner)              per resource            (WP-214 P3, P4)
                               (WP-73 Phase 2)
```

## Связи с другими РП

```
WP-73 (Архитектура платформы)
  ├── ADR-IWE-008: ory_id как универсальный ID        ← фундамент
  ├── DP.D.034: Три оси доступа (Keto)                ← следующий слой
  └── WP-212 (Безопасность)
        ├── B4.13-B4.15: user_id фильтрация            ← DONE (ручная)
        ├── B4.16-B4.20: верификация на пользователях   ← in_progress
        └── B4.21+: Neon Authorize + GW + CI            ← ТЕКУЩЕЕ РЕШЕНИЕ

WP-215 (Разделение RU/мир)
  ├── source_region закладка                            ← совместимо
  └── При 2 Ory: canonical_ory_id поверх RLS           ← эволюция

WP-214 (Учёт персональных данных)
  ├── P3: Consent layer (Cedar)                         ← следующая фаза
  ├── P5: ReBAC (Keto)                                  ← следующая фаза
  └── P9: Audit trail                                   ← следующая фаза

WP-187 (Ory Gateway)
  └── JWT access_token_strategy                         ← blocking dependency

WP-121 (Contribution Economy)
  └── RLS на point_transactions, point_balances         ← scope
```

## Принципы (Data Governance P1-P13)

| Принцип | Как решение реализует |
|---------|----------------------|
| **P1** Centralize trust, decentralize data | Ory = centralized trust. Данные в Neon с RLS = decentralized access |
| **P3** Consent mandatory | Не реализован текущим решением → следующая фаза (Cedar) |
| **P7** Local-first | Pack на устройстве. RLS не затрагивает |
| **P8** Once-only (OwnerIntegrity) | user_id = ory_id единый. Не дублируется |
| **P9** Audit trail | Не реализован → следующая фаза |
| **P10** Infrastructure-first | RLS на уровне инфраструктуры (БД), не кода |
| **P12** Never collect all in one place | PII в Ory, community data в Neon. Разделение сохраняется |

## Фазы реализации

| Фаза | Что | Бюджет | Зависимость |
|------|-----|--------|-------------|
| **Ф0** | Проверить Ory Hydra JWT strategy | 1h | — |
| **Ф1** | Настроить Neon Authorize (JWKS от Ory) | 2h | Ф0 |
| **Ф2** | RLS-политики на существующих таблицах (documents, user_sources, digital_twin_state, point_transactions) | 4h | Ф1 |
| **Ф3** | Обновить MCP-сервисы: передавать JWT в Neon driver | 4h | Ф1 |
| **Ф4** | Gateway: блокировка без JWT для private MCP | 2h | — |
| **Ф5** | CI lint: RLS checker + PII column ban | 3h | — |
| **Ф6** | E2E тесты изоляции (как B4.13-B4.15) | 2h | Ф2, Ф3 |
| **Ф7** | source_region закладка в event-таблицах | 1h | — |

**Итого:** ~19h. При 5h/нед = ~4 недели (W16-W19).

---

*Создано: 2026-04-09. Автор: Церен + Claude (АрхГейт session).*
*Для согласования с командой: Андрей (архитектор), Дима/Ильшат (backend), Паша (DevOps).*
