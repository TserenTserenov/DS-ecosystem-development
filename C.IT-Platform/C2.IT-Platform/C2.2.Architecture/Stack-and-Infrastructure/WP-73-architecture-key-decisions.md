---
type: architecture-key-decisions
title: "Архитектура платформы Aisystant — ключевые решения (compact)"
status: draft
created: 2026-04-19
updated: 2026-04-19
audience: архитектор, команда ИТ-платформы
source: WP-73-aisystant-platform-architecture.md (полный ~2200 строк)
depends_on: WP-73, WP-183, WP-187, WP-212, WP-214, WP-215, WP-227, WP-228, WP-231, WP-232, WP-244, WP-250
---

# Архитектура платформы Aisystant — ключевые решения

> **Компактный экстракт** для архитектора и команды из полного документа [`WP-73-aisystant-platform-architecture.md`](WP-73-aisystant-platform-architecture.md) (~200 KB). Сюда вынесены **только принятые решения, открытые вопросы и статусы** — без мотивации, примеров, детального gap-анализа.
> **Зачем:** полный документ неудобно читать перед встречей. Этот — читается за 10 минут.
> **Как поддерживаем:** полный — source-of-truth, здесь — ссылка + краткая формулировка. Обновляется вручную после каждой встречи архитектора.

---

## 1. Архитектура 3 слоёв (DP.ARCH.001)

```
Слой 3 — Интерфейсы (thin clients): Telegram Bot, Web LMS (Java/Vaadin),
         Discourse (клуб), Claude Code CLI, Web App (Vue/Nuxt, planned).

Слой 2 — Обработка (peer-to-peer):
  Zone A (AI, stateless):  Стратег, Экстрактор, Консультант, Проводник,
                           Оценщик, Наладчик, Статистик.
  Zone B (code, stateful): Digital Twin MCP, Knowledge MCP, Guides MCP,
                           Composer MCP, LMS, Billing (planned),
                           ORY (identity), CRM (planned), Activity Hub.

Слой 1 — Данные + Инфра:  Neon PostgreSQL (pgvector), GitHub (25+ repo),
                           Railway (бот), Cloudflare Workers (MCP).
```

**Ключевое различение (WP-247, Pack DP.D.048):** Zone A — «агент» (LLM выбирает шаг), Zone B — «скрипт» (фиксированный control flow). Оба исполняют роли, отличаются только механикой.

---

## 2. Карта подсистем (20, статус на 19 апр)

| # | Система | Статус | Ключевое |
|---|---------|--------|----------|
| 1 | Digital Twin (digital-twin-mcp) | 🟡 | Profiler standalone (WP-218). Унификация user_id (WP-227 DONE) |
| 2 | LMS Aisystant | ✅ | Java 8 / Vaadin 8 монолит (**не трогаем**, ADR-012) |
| 3 | Клуб Discourse | ✅ | Сообщество |
| 4 | CRM + Payment Registry | 🟡 MVP | Directus + Metabase. Целевое: **БД #4 payment-registry** (WP-228 ArchGate 19 апр) |
| 5 | Реестр подписок `subscription_grants` | ✅ | Единый источник истины, GHA cron 30 мин. 2740/771 активных (WP-231) |
| 6 | Knowledge MCP | ✅ | 5400+ docs, 9 sources, RLS |
| 7 | Activity Hub | 🟡 ~70% | Platform-журнал событий (ADR-009). 4 адаптера: LMS, Bot, Git, WakaTime |
| 8 | Проводник (Route Guide AI) | ❌ planned | Маршрутизация по ЦД |
| 9 | MCP Hub / Gateway | ✅ MVP | `mcp.aisystant.com`, Ory auth, 3 remote MCP. Subscription check на уровне tool call |
| 10 | ORY Identity | ✅ | OAuth2, RS256 JWT (kid="" fixed). **ory_id = единственный ID** (ADR-IWE-008) |
| 11 | Proof-of-Impact (баллы) | 🟡 Ф1 | points.* schema, 38 rules + 8 qual (WP-121). calculate_points() pending |
| 12 | Concept Graph | 🟡 MVP | 3503 рёбра, 1180 понятий. Bilingual (WP-242) |
| 13 | Бот Aist | ✅ | aiogram, RLS на 5 таблицах |
| 14 | SystemsSchool_bot | ✅ | TG-бот расписаний (read-only) |
| 15 | Personal Knowledge MCP | ✅ | Pack CRUD, zero-git onboarding (WP-187) |
| 16 | AI-системы (DS-ai-systems) | ✅ | Монорепо 7 ролей |
| 17 | Публикатор клуба | ✅ | Content Pipeline → TG/клуб (WP-155 MVP 24 апр) |
| 18 | Platform Health (DB #8) | 🟢 ArchGate пройден | uptime, инциденты, anthropic-status (WP-244). Публичная status page — **готовый SaaS**, не своя |
| 19 | Profiler (recalculate_derived.py) | ✅ | Standalone, 112/112 (WP-218) |
| 20 | Content Pipeline (DB #9) | 🟡 проектирование | MVP 24 апр: text→TG, tenant=Tseren (WP-155) |

**MAP.002 сервисов:** 65+ service clauses. Ключевые: SC.112 (Gateway), SC.114 (Subscription Check), SC.115 (Позиционирование).

---

## 3. Целевая архитектура БД: 9 Neon-баз (WP-228, ArchGate 19 апр)

| # | База | Назначение | Статус |
|---|------|------------|--------|
| 1 | `platform` | identity + subscription_grants + points + knowledge | ✅ работает |
| 2 | `knowledge` | Knowledge Base (L2 платформенные знания) | ✅ (выделен при консолидации) |
| 3 | `activity-hub` | Event Sourcing, Write-heavy | 🟡 проектирование |
| 4 | `payment-registry` | finance.*, crm.* (YooKassa, Stripe, Stars) | 🟡 проектирование (WP-183 переезд) |
| 5 | `digital-twin` | user_events, projections | 🟡 (WP-227 переход) |
| 6 | `aist-bot` | state machine + 35+ tables | ✅ legacy |
| 7 | `metabase` | BI (вытесняет Directus-analytics) | 🟡 |
| 8 | `health` | uptime, incidents, anthropic-status (ADR-IWE-013) | 🟢 ArchGate пройден |
| 9 | `content-pipeline` | публикации, токены соц.сетей (payment_credentials class) | 🟡 MVP |

**Принципы размещения:**
1. **PII, payment_credentials, токены соц.сетей** — строго изолированы.
2. **Bot = интерфейс**, не место доменных сущностей (HD #39).
3. **Одна база `platform`** для cross-domain joins (points ↔ subscriptions).
4. **Metabase ≠ схема в platform** (blast-radius, bounded context).

---

## 4. ADR — архитектурные решения (консолидированная таблица)

> ✅ принято, 🔶 предлагается (требует согласования), ⏸️ отложено.

### 4.1. Принятые (фундамент)

| # | Решение | Дата | Ref |
|---|---------|------|-----|
| ADR-001 | Multi-surface с Web-ядром (Vue/Nuxt) | 29 мар | 69/80 |
| ADR-002 | Event Sourcing для ЦД (immutable events + 5 проекций) | — | 8.7 |
| ADR-003 | Role-centric архитектура (роль ≠ исполнитель, DP.D.033) | — | 50/60 |
| ADR-004 | Neon PostgreSQL единая СУБД (отказ от SurrealDB) | — | — |
| ADR-005 | Railway → Kubernetes (позже) | 19 фев | — |
| ADR-006 | ORY Network для SSO (PKCE flow) | — | — |
| ADR-009 | Activity Hub = платформенный журнал событий (pg_notify транспорт) | 29 мар | — |
| ADR-010 | RLS для изоляции данных | 29 мар | — |
| ADR-012 | LMS не трогаем, новая архитектура рядом | 29 мар | — |
| ADR-014 | Трёхосевая модель: Permission = Entitlement ∩ Role ∩ Scope | — | 8.7 |
| ADR-IWE-003 | Gateway Backend Interface (KG-01..KG-13) | — | 9.1 |
| ADR-IWE-004 | GitHub App Installation Token (per-repo, 1h TTL) | — | — |
| ADR-IWE-005 | ingest_event: Personal Knowledge → Activity Hub напрямую | — | — |
| ADR-IWE-006 | Async Write Pattern (<100ms ответ, ~5s коммит) | — | — |
| ADR-IWE-008 | **Identity: ory_id как единственный универсальный ID** | 7 апр | — |
| ADR-IWE-009 | Neon: одна база `platform` со схемами (консолидация 4→1) | 12 апр | WP-232 |
| ADR-IWE-010 | MCP-безопасность: двухшаговая модель (SET LOCAL + JWKS) | 13 апр | — |
| ADR-IWE-011 | `subscription_grants` — единый источник истины подписок | 13 апр | WP-231 |
| ADR-IWE-012 | Вариант E (MCP independent JWT verification, RS256) | 14 апр | — |
| ADR-IWE-013 | DB #8 `health` — наблюдаемость изолирована от PII | 15 апр | WP-244 |
| ADR-IWE-014 | Neon: 9 баз (целевое) при масштабировании | 19 апр | WP-228 |

### 4.2. Предлагаемые (требуют обсуждения)

| # | Решение | Что утверждаем |
|---|---------|----------------|
| ADR-007 | Двойной деплой RU + EU | Два сайта, единый бэкенд. **Q2 режим: заморожено** (WP-215, решение 19 апр) |
| ADR-008 | Billing через Strategy pattern | YooKassa + Stripe + Stars, единая логика |
| ADR-011 | TG-группы для команд | Аудитория уже в Telegram (P16) |
| ADR-013 | «Банковское приложение» UX | Привычка ежедневной проверки |
| ADR-015 | Образованные агенты (fine-tuning на ZP/FPF) | Синтетические данные |
| ADR-016 | JWT-based доступ к семинарам/вебинарам | Персональные JWT-ссылки только оплатившим |
| ADR-017 | LLM Multi-Provider Fallback (shared library) | Claude → OpenAI fallback. Embeddings — без fallback |
| ADR-018 | MCP Hub (Registry + Gateway + Provisioner, три типа MCP) | Поглощает Apps SDK |
| ADR-IWE-007 | Content Integrity при индексации | Exclusion list, manifest hash pinning |

---

## 5. Открытые вопросы (для архитектора / команды)

### Для архитектора

| # | Вопрос | Статус |
|---|--------|--------|
| Q5 | Discourse SSO (DiscourseConnect + ORY?) | Не обсуждался 29 мар |
| Q6 | Каналы для команд (SC-8) | Открыт |
| Q13 | Репликация данных RU↔EU | 🔶 2 базы + механизм синхронизации (29 мар). **Q2 заморожено** |
| Новое | ER-диаграммы 9 БД (только физ.объекты, не отношения) | WP-228 Ф9, к встрече ~21 апр |
| Новое | Процесс аудита изменений безопасности | WP-212 B7.5, запрос Tseren |
| Новое | Ревьюер архитектуры безопасности (Паша — B7.3) | WP-212 |
| Новое | Внешний human-аудит (B7.4) | WP-212, по запросу |

### Для юридической консультации

| # | Вопрос |
|---|--------|
| Q9 | 152-ФЗ: точный scope локализации ПД граждан РФ |
| Q11 | Санкционный compliance: автоматическая проверка? |
| ~~Q14~~ | Два юрлица (РФ + международное). **Решено:** ИП (РФ) + Aisystant Corp (USA). Stars — через Телеграм (физ.лицо) |

### Бизнес-решения

| # | Вопрос |
|---|--------|
| Q12 | Выбор РФ-хостинга (Hetzner Russia vs VK Cloud vs Selectel) |
| C4 | Unit economics по тирам |
| C6 | 25 репо → масштабируемость |

---

## 6. Q2 2026 режим (решение 19 апр)

> **Гипотеза массового продукта через подписку** (WP-250): пока её не подтвердили, **инфраструктуру не развиваем, поддерживаем под MVP**.

| РП | Q2 режим | Примечание |
|----|----------|------------|
| WP-73 | **поддержание** | документ живёт, решения принимаем по запросу |
| WP-183 | **MVP** | payment-registry DB #4 — портируем YooKassa/Stripe/Stars |
| WP-187 | **MVP** | Knowledge Gateway до фиксации MVP |
| WP-212 | **поддержание** | RLS раскатана. B7 (аудит безопасности) — по запросу |
| WP-215 | **frozen** | дуальный контур РФ/мир — до подтверждения гипотезы массового продукта |
| WP-228 | **active** | карта данных + ER-диаграммы Ф9 |
| WP-244 | **active** | DB #8 health + Grafana + публичная status page (SaaS) |

---

## 7. Ссылки

- **Полный документ:** [WP-73-aisystant-platform-architecture.md](WP-73-aisystant-platform-architecture.md) (~200 KB)
- **Концепция использования:** [WP-74-platform-concept-of-use.md](WP-74-platform-concept-of-use.md)
- **Повестка встреч архитектора:** [WP-73-architect-agenda-next.md](WP-73-architect-agenda-next.md)
- **Данные (9 БД):** [PACK-digital-platform/02-domain-entities/DP.ARCH.004-neon-data-architecture.md](../../../../PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.004-neon-data-architecture.md)
- **Принципы платформы:** [DP.ARCH.001-platform-architecture.md](../../../../PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.001-platform-architecture.md) §7
- **Сервисы (service clauses):** [PACK-digital-platform/08-service-clauses/](../../../../PACK-digital-platform/pack/digital-platform/08-service-clauses/)
- **Стратегический контекст:** [DS-my-strategy/inbox/WP-250-plan-2026.md](../../../../DS-my-strategy/inbox/WP-250-plan-2026.md)
