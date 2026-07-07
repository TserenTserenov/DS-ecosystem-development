<!-- index-health: skip -->
<!-- Обоснование: рабочий inbox-индекс документов; длинные строки = URL/пути, не дамп контекста. -->
# Индекс документов платформы Aisystant и системы IWE (post-MVP)

---

## 1. Позиционирование и ценность

| # | Документ | Что внутри | Канон |
|---|----------|-----------|-------|
| 1.1 | **Уникальность IWE** | 5 природ IWE (Мастерская, Железный человек, Аватар, Тамагочи, Наставник). Фундаментальная формулировка. Запрещённые слова. Черновик у Тсерена, требует запроса доступа. | — |
| 1.2 | **Brand Foundations** | Onliness v0.2, 5 природ в таблице, JTBD, архетип Sage+Creator, ценности, антипозиционирование. | `DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.1.Meaning/2.1.1. Brand/01-foundations.md` |
| 1.3 | **Обещание и сценарии** | 5 гарантий платформы. 10 ролей + сценарии использования (Новичок → Организатор групп). | `DS-ecosystem-development/0.OPS/0.9.Inbox/WP-336-обещание-и-сценарии.md` |
| 1.4 | **Стратегия экосистемы 2026** | Операционная цель: пивот от курсов к платформе+IWE. Формула. Стратегические инварианты. Окно момента. | `DS-ecosystem-development/A.Systems-Builder/A3.Aisystant-Ecosystem-Builder/A3.1.Meaning/3.1.2. Strategy-2026/Стратегия экосистемы 2026.md` |
| 1.5 | **Манифест созидателей** | Видение, философия, архетипы сообщества. | `DS-ecosystem-development/B.Aisystant-Ecosystem/B1.Society/B1.1.Meaning/1.1.0. Manifesto/Манифест созидателей.md` |

---

## 2. Пользовательская концепция

| # | Документ | Что внутри | Канон |
|---|----------|-----------|-------|
| 2.1 | **Концепция использования v2.0** | Перезаписанная концепция: 10 ролей, 6 измерений мастерства, 5 гарантий, Knowledge Gateway, Parliament Model, сравнение v1.0→v2.0. | `DS-ecosystem-development/A.Systems-Builder/A3.Aisystant-Ecosystem-Builder/A3.2.Architecture/3.2.1. IT-Platform-Concept/Концепция использования ИТ-платформы Aisystant 3.2.md` |
| 2.2 | **Принципы взаимодействия** | UX-принципы: экзоскелет≠протез, прозрачность ИИ, постепенное раскрытие, data ownership. | `DS-ecosystem-development/A.Systems-Builder/A3.Aisystant-Ecosystem-Builder/A3.2.Architecture/3.2.1. IT-Platform-Concept/Принципы взаимодействия человека с платформой 3.2.md` |
| 2.3 | **Onboarding** | IWE Quickstart, что такое IWE, настройка браузера, VS Code setup, персональное руководство. | `DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.1.Meaning/2.1.2. Onboarding/` |

---

## 3. Архитектура (техническая)

### 3.1. Общая архитектура и принципы

| # | Документ | Что внутри | Канон |
|---|----------|-----------|-------|
| 3.1.1 | **Общая архитектура ИТ-платформы** | 3-слойная модель, принципы, сравнение as-is→to-be. | `DS-ecosystem-development/A.Systems-Builder/A3.Aisystant-Ecosystem-Builder/A3.2.Architecture/3.2.2. Architectural-Decisions/Общая архитектура ИТ-платформы 3.2.md` |
| 3.1.2 | **Карта ИТ-систем** | 14+ детерминированных систем, AI-ассистенты, AI-агенты. | `DS-ecosystem-development/A.Systems-Builder/A3.Aisystant-Ecosystem-Builder/A3.2.Architecture/3.2.2. Architectural-Decisions/Карта ИТ-систем 3.2.md` |
| 3.1.3 | **Контуры системы** | Platform Contours — высокоуровневые границы системы. | `DS-ecosystem-development/0.OPS/0.1.Knowledge-Logic/11-platform-contours.md` |
| 3.1.4 | **Архитектура платформы IWE (для Андрея)** | Data Layers (Персона/Память/Контекст), Parliament Model, Event Sourcing, 6 измерений мастерства. | `DS-ecosystem-development/0.OPS/0.9.Inbox/WP-336-архитектура-платформы-iwe.md` |

### 3.2. Pack — формализованная спецификация

| # | Документ | Что внутри | Канон |
|---|----------|-----------|-------|
| 3.2.1 | **Platform ontology** | Онтология платформы (DP.ONT.001). | `PACK-digital-platform/pack/digital-platform/01-domain-contract/DP.ONT.001-platform-ontology.md` |
| 3.2.2 | **Platform architecture** | DP.ARCH.001 — 25 принципов, покрытие характеристик. | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.001-platform-architecture.md` |
| 3.2.3 | **Digital Twin architecture** | DP.ARCH.003 — Events→State→Views, Persona/Memory/Context. | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.003-digital-twin-architecture.md` |
| 3.2.4 | **Neon data architecture** | DP.ARCH.004 v2.4+ — 12 БД, схемы, migration roadmap. | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.004-neon-data-architecture.md` |
| 3.2.5 | **IWE — Intelligent Working Environment** | DP.IWE.001 — определение, границы, интерфейсы. | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.IWE.001-intelligent-working-environment.md` |
| 3.2.6 | **Five natures of IWE** | DP.IWE.007 — 5 природ: Мастерская, Железный человек, Аватар, Тамагочи, Наставник. | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.IWE.007-five-natures-iwe.md` |
| 3.2.7 | **IWE Service Catalog** | DP.MAP.002 — 56 сервисов, роли, триггеры, маппинг на SC. | `PACK-digital-platform/pack/digital-platform/07-map/DP.MAP.002-iwe-service-catalog.md` |
| 3.2.8 | **Platform concept** | DP.CONCEPT.001 — концепция платформы (formal). | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.CONCEPT.001-platform-concept.md` |
| 3.2.9 | **IWE layer portability** | DP.D.056 — переносимость слоёв IWE. | `PACK-digital-platform/pack/digital-platform/01-domain-contract/DP.D.056-iwe-layer-portability.md` |
| 3.2.10 | **Role-centric architecture** | DP.D.033 — архитектура вокруг ролей, не исполнителей. | `PACK-digital-platform/pack/digital-platform/01-domain-contract/DP.D.033-role-centric-architecture.md` |

### 3.3. Архитектурные решения (ADR)

| # | ADR | Тема | Путь |
|---|-----|------|------|
| ADR-001 | Multi-surface Web UI | Vue/Nuxt.js как каноническая поверхность | `PACK-digital-platform/.../01D-adr-web-ui-platform.md` |
| ADR-IWE-003 | Gateway Backend Interface | Контракт MCP-серверов за Gateway | `DS-ecosystem-development/.../ADR-IWE-003-gateway-backend-interface.md` |
| ADR-IWE-008 | Identity ORY ID Universal | `ory_id` = единственный универсальный ID | `DS-ecosystem-development/.../ADR-IWE-008-identity-ory-id-universal.md` |
| ADR-IWE-010 | MCP Security | Двухшаговая модель: RLS + JWT | `DS-ecosystem-development/.../ADR-IWE-010-mcp-security.md` |
| ADR-IWE-012 | MCP Independent JWT Verification | Каждый MCP верифицирует JWT самостоятельно | `DS-ecosystem-development/.../ADR-IWE-012-mcp-independent-jwt-verification.md` |
| ADR-IWE-014 | L2/L3 Boundary | Граница open-core L2/L3 | `DS-ecosystem-development/.../ADR-IWE-014-l2-l3-boundary.md` |
| ADR-IWE-015 | OAuth Gateway Extraction | Выделение OAuth gateway | `DS-ecosystem-development/.../ADR-IWE-015-oauth-gateway-extraction.md` |

### 3.4. Детерминированные системы

| # | Система | Описание | Путь |
|---|---------|----------|------|
| S1 | Цифровой двойник | Persona/Memory/Context, Event Sourcing, 5 проекций | `A3.2.Architecture/3.2.3.1. Цифровой двойник/` |
| S2 | Хаб активностей | Activity Hub, 50 типов событий, medallion arch | `A3.2.Architecture/3.2.3.2. Хаб активностей/` |
| S3 | CRM | Directus + Metabase, 35879 строк | `A3.2.Architecture/3.2.3.3. CRM/` |
| S4 | LMS | Платформа обучения (Java/Vaadin → API-обёртка) | `A3.2.Architecture/3.2.3.4. LMS и обучение/` |
| S5 | Клуб | Discourse, сообщество | `A3.2.Architecture/3.2.3.5. Клуб/` |
| S6 | Управление кейсами | Case management | `A3.2.Architecture/3.2.3.6. Управление кейсами/` |
| S7 | Единое хранилище | Knowledge MCP, 5400+ docs | `A3.2.Architecture/3.2.3.7. Централизованное хранилище/` |
| S8 | Система рабочих сред | Система IWE, оркестрация | `A3.2.Architecture/3.2.3.8. Операционная система ИТ-платформы/` |
| S9 | Идентификация (ORY) | ORY Kratos/Hydra, SSO, JWT | `A3.2.Architecture/3.2.3.9. Идентификация и доступ (ORY)/` |
| S10 | Биллинг | Подписки, платежи, revenue sharing | `A3.2.Architecture/3.2.3.10. Биллинг и оплата/` |
| S11 | Приём оплаты | YooKassa, Stripe, TG Stars | `A3.2.Architecture/3.2.3.11. Системы приёма оплаты/` |
| S12 | Распределитель токенов | Баллы, лояльность | `A3.2.Architecture/3.2.3.12. Распределитель токенов/` |
| S13 | Эпистемический граф | Concept Graph, 3503 рёбра | `A3.2.Architecture/3.2.3.13. Эпистемический граф/` |
| S14 | Apps SDK и маркетплейс | MCP Hub, Community MCP | `A3.2.Architecture/3.2.3.14. Apps SDK и маркетплейс/` |

### 3.5. ИИ-системы

| # | Система | Роль | Путь |
|---|---------|------|------|
| AI-1 | Проводник | Route Guide, маршрутизация по ЦД | `A3.2.Architecture/3.2.4. AI-Assistants/3.2.4.1. Проводник/` |
| AI-2 | Генератор инфопродуктов | Content generation | `A3.2.Architecture/3.2.4. AI-Assistants/3.2.4.2. Генератор инфопродуктов/` |
| AI-3 | ДЗ-чекер | Проверка домашних заданий | `A3.2.Architecture/3.2.4. AI-Assistants/3.2.4.3. Проверяльщик ДЗ/` |
| AI-4–14 | ИИ-агенты (11) | Orchestrator, Librarian, Docs, ConsistencyChecker и др. | `A3.2.Architecture/3.2.5. AI-Agents/` |

---

## 4. Инфраструктура и инженерия

| # | Документ | Что внутри | Канон |
|---|----------|-----------|-------|
| 4.1 | **Track B — международная инфраструктура** | GKE Standard, Cloud SQL, приватная сеть, Werf, Terraform. Отдельный документ, требует запроса доступа у Тсерена. | — |
| 4.2 | **Deployment-диаграмма** | C4 L3, топология, провайдеры. | `DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Stack-and-Infrastructure/deployment.md` |
| 4.3 | **Соответствие облачным требованиям (12-factor)** | Аудит: 92% закрыто. Отдельный документ, требует запроса доступа у Тсерена. | — |
| 4.4 | **Security posture** | STRIDE-анализ, ротация ключей, карта персональных данных. | `DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Identity-and-Access/` |
| 4.5 | **Observability** | status.aisystant.com, Better Stack, Grafana. Отдельный документ, требует запроса доступа у Тсерена. | — |
| 4.6 | **Реестр репозиториев** | 22 активных репо, типы, назначения. | `DS-ecosystem-development/0.OPS/REPOSITORY-REGISTRY.md` |
| 4.7 | **Инвентарь сервисов** | 16 CF Workers + Python, 16 БД, матрица ответственности. | `DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/WP-285-services-inventory.md` |
| 4.8 | **Концепция разделения Россия/Мир** | Топология организаций GitHub, язык, финансы, что разделяется/что общее, конвейер канон→проекции, табло репозиториев на приватизацию. | `DS-ecosystem-development/0.OPS/0.9.Inbox/WP-415-russia-world-split-concept.md` (+ `WP-415-migration-plan.md`, `WP-415-pipeline-architecture.md`, `WP-415-iwe-sync-conventions.md`, `WP-415-object-tiering-model.md`) |

---

## 5. Питчи и инвестиции

| # | Документ | Что внутри | Канон |
|---|----------|-----------|-------|
| 5.1 | **Pitch Deck v0.6** | «Дистрибутив интеллекта» — продукт-first, ownership, Ubuntu-модель. | `DS-ecosystem-development/A.Systems-Builder/A3.Aisystant-Ecosystem-Builder/A3.1.Meaning/3.1.1. Investment-Attraction/pitch/v0.6/DECK.md` |
| 5.2 | **Elevator v0.5** | 5 предложений, ~30 сек. | `DS-ecosystem-development/.../pitch/v0.6/ELEVATOR.md` |
| 5.3 | **Варианты питчей** | Альтернативные формулировки под разные аудитории. | `DS-ecosystem-development/.../A3.1.Meaning/Варианты питчей 3.1.md` |
| 5.4 | **Позиционирование продукта** | Для инвесторов: что, для кого, почему мы. | `DS-ecosystem-development/.../A3.1.Meaning/Позиционирование продукта 3.1.md` |
| 5.5 | **Executive Summary** | Краткое описание экосистемы для инвесторов. | `DS-ecosystem-development/.../A3.1.Meaning/Executive Summary 3.1.md` |
| 5.6 | **Pitch Deck v0.7** | Обновлённый: 5 природ, специальность, «Железный человек». | `DS-ecosystem-development/.../pitch/v0.7/` *(в работе)* |

---

## 6. Планы развития и дорожные карты

| # | Документ | Что внутри | Канон |
|---|----------|-----------|-------|
| 6.1 | **Neon migration roadmap** | DP.ROADMAP.001 — фазы миграции Neon. | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ROADMAP.001-neon-migration.md` |
| 6.2 | **MVP greenfield roadmap** | DP.ROADMAP.002 — MVP с чистого листа. | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ROADMAP.002-mvp-greenfield.md` |
| 6.3 | **Roadmap архитектуры платформы** | 4 фазы (март 2026 → 2027+), 22 ключевых изменения. | `DS-ecosystem-development/0.OPS/0.99.Archive/WP-73-aisystant-platform-architecture.md` §3.3 |
| 6.4 | **Приложение 8. План работ** | Задачи по службам из Стратегии 2026. | `DS-ecosystem-development/.../A3.1.Meaning/3.1.2. Strategy-2026/Приложение 8. План работ.md` |
| 6.5 | **Направления плана развития** | Инфраструктура, IWE, AI, экосистема, маркетинг (архив, направления теперь живут в стратегии Тсерена). | `DS-ecosystem-development/0.OPS/0.99.Archive/WP-336-development-directions.md` |

---

## 7. Активные направления работы (координация)

> Рабочие материалы и текущий статус по каждому направлению ведёт Тсерен в личной рабочей area - здесь только список для общей картины, за деталями обращаться напрямую.

| Направление | Статус | Что координирует |
|----|--------|-----------------|
| Архитектурный план ИТ-платформы | в работе | каталог документов → канон, регламент передачи знания, финальная сверка |
| Упаковка ценности IWE | закрыто | 5 природ IWE - знание перенесено в канон платформы (`PACK-digital-platform`) |
| Концепция использования платформы | закрыто | пользовательская концепция (архив: `DS-ecosystem-development/0.OPS/0.99.Archive/WP-74-platform-concept-of-use.md`) |
| Пост-манифесто | в работе | уникальность IWE, позиционирование |
| Бренд IWE | в работе | брендинг и вербальная идентичность |
| Track B — международная инфраструктура | в работе | GKE, Cloud SQL (детали - см. §4.1) |
| Multi-Agent IWE | в работе | взаимодействие нескольких ИИ-помощников, локальный шлюз, оркестрация |
| Архитектура Neon | в работе | база данных платформы: реализация, приём событий, обработка проекций |

---

## 8. Чеклист: что должно быть описано для полноты картины

### 8.1. Архитектура 
- [x] Общая архитектура (3 слоя, принципы) — §3.1.1
- [x] Карта систем (14+ детерминированных + ИИ) — §3.1.2
- [x] Data architecture (Neon, 12 БД) — §3.2.4
- [x] Digital Twin (Event Sourcing, проекции) — §3.2.3
- [x] MCP Hub / Gateway — §3.4. S14
- [x] Identity (ORY) — §3.4. S9
- [x] ADR (7+ принятых) — §3.3

### 8.2. Пользовательская концепция 
- [x] 10 ролей пользователей — §2.1
- [x] 6 измерений мастерства — §2.1
- [x] 5 гарантий платформы — §1.3
- [x] Сценарии использования по ролям — §2.1
- [x] Принципы взаимодействия — §2.2

### 8.3. Позиционирование 
- [x] 5 природ IWE — §1.1
- [x] Onliness statement — §1.2
- [x] JTBD — §1.2
- [x] Слоган T6 — §1.1
- [x] Запрещённые слова — §1.1

### 8.4. Инфраструктура 
- [x] Track A (текущая: CF Workers + Neon + Railway) — §4.6
- [x] Track B (GKE Standard + Cloud SQL + приватная сеть) — §4.1
- [x] 12-factor compliance — §4.3
- [x] Security (B7.3, STRIDE) — §4.4
- [x] Observability — §4.5

### 8.5. Бизнес-модель 
- [x] Стратегия экосистемы 2026 — §1.4
- [x] Тарифы и пакеты — `A2.1.Meaning/2.1.1. Продуктовые предложения/`
- [x] Экономика экосистемы — `B3.1.Meaning/Экономика экосистемы 3.1.md`
- [x] Unit-экономика — `Приложение 5. Unit-экономика.md`

### 8.6. Питч  (needs update)
- [x] Pitch v0.6 — §5.1 (устарел: 4 природы, старый нарратив)
- [ ] **Pitch v0.7** — §5.6 (в работе: 5 природ, специальность, «Железный человек»)

### 8.7. План развития  (needs formalization)
- [x] Roadmap миграции Neon — §6.1
- [x] Roadmap MVP greenfield — §6.2
- [ ] **Направления плана развития** — §6.5 (в работе)

---

## 9. Как использовать этот индекс

1. **Новый участник команды** → начни с §1 (позиционирование) → §2 (концепция) → §3.1 (общая архитектура)
2. **Архитектор / разработчик** → §3 (вся архитектура) → §4 (инфраструктура) → Pack §3.2
3. **Инвестор** → §5 (питчи) → §1.4 (стратегия) → §8.5 (бизнес-модель)
4. **Продукт / UX** → §2 (концепция) → §3.5 (ИИ-системы) → §1 (позиционирование)
5. **При проверке полноты картины архитектуры** → §8 (чеклист полноты) → §7 (активные направления работы)

---
