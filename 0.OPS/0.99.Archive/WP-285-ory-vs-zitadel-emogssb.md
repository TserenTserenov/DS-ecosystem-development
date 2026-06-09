---
type: doc
status: archived
archived_date: 2026-06-09
created: 2026-05-22
updated: 2026-05-22
family: F8
kernel: C
system: C2
role: Architecture
author: Церен
target_audience:
  - Андрей
  - Паша
  - Тсерен
  - Ильшат
related:
  - WP-285-decisions-registry.md
  - WP-285-track-b-plan.md
  - WP-285-services-inventory.md
tags:
  - idp
  - ory
  - zitadel
  - archgate
  - track-b
---

# Track B IdP: Ory vs Zitadel — профиль ЭМОГССБ

> **Контекст:** Track B = новый деплой мировой платформы Aisystant на GKE Standard (europe-west4) + Cloud SQL + Stripe. Решение принимается на встрече 24 мая 2026. Для Track A (Россия) IdP не пересматриваем — там Ory остаётся как есть.
>
> **Вопрос встречи:** ставим ли для Track B Zitadel (single binary, B2B-ориентированный) или сохраняем Ory (Kratos + Hydra; Keto/Oathkeeper в Track A фактически не задействованы).
>
> **Метод:** conjunctive screening по 7 характеристикам ЭМОГССБ (см. `.claude/skills/archgate/SKILL.md`). Один ❌ = блокирует выбор.

---

## 1. Резюме (TL;DR)

**Рекомендация: Ory (Kratos + Hydra) для Track B.**

1. У Ory **нет ни одного ❌**; у Zitadel **один блокирующий ❌** — отсутствие RFC 7591 (DCR) и RFC 8707 (Resource Indicators), без которых ломается OAuth-флоу gateway-mcp для claude.ai/ChatGPT (Zitadel в документации явно отклоняет запросы с параметром `resource`).
2. Стоимость переключения для Паши = 0 (Ory он уже знает; обучение Zitadel ~2-3 недели против известного стека). Track A не трогаем — риск downtime в РФ = 0 в обоих сценариях.
3. Аргумент Zitadel «native multi-tenancy» нерелевантен: Track B стартует одним тенантом (мировая платформа Aisystant), а тiер-модель подписок (DP.ARCH.002) реализуется одинаково через claims в обоих стеках.
4. У Zitadel в 2025 году опубликовано 13 CVE (включая SSRF, account-takeover, brute-force lockout disabled by default) — security-track record на свежем мажоре 4.x хуже, чем у зрелого Ory.
5. **Условие пересмотра:** появление в Zitadel RFC 7591 + RFC 8707 (issue открыт, не closed) **И** независимая B2B-multi-tenancy потребность (отдельные IdP per enterprise customer) — тогда вернуться к сравнению в H2 2026.

---

## 2. Таблица 7×3

| # | Характеристика | Ory (Kratos + Hydra) | Zitadel (single binary) |
|---|----------------|----------------------|--------------------------|
| Э | Эффективность (ресурсы, ops) | ⚠️ | ⚠️ |
| М | Масштабируемость (14 → 10k+) | ✅ | ✅ |
| О | Открытость (OSS, стандарты) | ✅ | ⚠️ |
| Г | Готовность (MCP, prod-refs, UI) | ✅ | ❌ |
| С1 | Стабильность (CVE, breaking changes) | ✅ | ⚠️ |
| С2 | Совместимость (social, passkey, linking) | ✅ | ✅ |
| Б | Безопасность (GDPR, audit, MFA, brute-force) | ✅ | ⚠️ |

**Conjunctive screening:** Ory 0 × ❌; Zitadel 1 × ❌ (Готовность). **Zitadel не проходит экран.**

---

## 3. Детальный разбор

### 3.1. Э — Эффективность ⚠️ / ⚠️

**Ory (⚠️):** Hydra — 1 vCPU / 1-2 GB RAM на инстанс при малой нагрузке; Kratos лёгкий («very lightweight» в официальных доках, без жёстких минимумов). Минус — **4 микросервиса** в манифестах (Kratos + Hydra + Keto + Oathkeeper), даже если используется только 2 из 4 в Track A. Ops-нагрузка: больше Helm-чартов, больше ingress-rules. Прозрачное решение — деплоить только Kratos + Hydra на Track B (Keto/Oathkeeper не разворачивать). Лицензия — Apache 2.0 для open-source бинарей; Ory Enterprise License (OEL) — платная, для prod-builds.

**Zitadel (⚠️):** Single binary, минимум ~512 MB RAM + <1 vCPU на «лёгкий» сетап. Но production-рекомендация — HA-кластер из 3 нод × 4 vCPU × 16 GB RAM (или 4×8 в экономном режиме), плюс CPU-spike при хешировании паролей требует ≥4 vCPU. То есть «одно бинарное» внешне — но prod-footprint сопоставим с Ory. **Лицензия изменена в начале 2025: Apache 2.0 → AGPL 3.0** — для прямого распространения форка или SaaS-on-top это блокер; для self-hosted Track B по умолчанию ОК, но при возможных будущих дистрибутивах (managed-канал для клиентов) AGPL ограничивает.

Итог: ни у одного нет явного преимущества по cost/ops. Обоим ⚠️ — оба требуют DevOps-внимания. Ory чуть выигрывает по «не нужно сразу 3-нодный HA».

### 3.2. М — Масштабируемость ✅ / ✅

**Ory (✅):** Доказанная масштабируемость до миллионов запросов/сутки. OpenAI публично использует Ory Hydra. Архитектура stateless (Postgres-backed), горизонтальное масштабирование «тысячи подов без перенастройки». Под 14 → 10k users Track B — запас огромный.

**Zitadel (✅):** Event-storing архитектура, поддержка CockroachDB и Postgres, линейное горизонтальное масштабирование. Заявленные миллионы пользователей в B2B-сценариях.

Оба ✅. На целевых объёмах (10k users) разница нерелевантна.

### 3.3. О — Открытость ✅ / ⚠️

**Ory (✅):** Apache 2.0 на ядро (Kratos, Hydra, Keto, Oathkeeper); OEL — отдельная коммерческая надстройка, без неё OSS-сборки полностью функциональны. Стандарты: OIDC certified, OAuth 2.1, SAML, SCIM, FIDO2/WebAuthn. Github stars Kratos ~12k, Hydra ~16k. Возможность форка — без ограничений.

**Zitadel (⚠️):** **AGPL 3.0 с 2025** — обязывает open-source производные сервисы. Github stars ~10k. OIDC, OAuth 2.0 (не 2.1 в новых deepest-cases, см. DCR), SAML, SCIM. Форк возможен, но AGPL-наследование ограничивает коммерческие сценарии «оборачивания» в собственный SaaS. Сообщество активное, но в разы меньше комбинированной Ory community + OpenAI/Auth0-выпускников.

### 3.4. Г — Готовность ❌ (Zitadel)

**Ory (✅):** Hydra — OpenID Certified™ provider, используется OpenAI и другими в продакшене. **RFC 7591 (DCR)** — issue #1616 закрыт, поддержка реализована (есть production-deployments gateway-mcp на Hydra с DCR-flow для Claude Code / ChatGPT, см. блог-пост getlarge.eu). **RFC 8707 (Resource Indicators)** — поддерживается. То есть **текущая интеграция Ory + gateway-mcp на Cloudflare Workers** работает без архитектурного редизайна. UI: Ory Account Experience + headless Kratos API + Ory Console для админки. Migration-path для Track B — копируем существующий код gateway-mcp, меняем `ORY_URL` → новый EU-инстанс.

**Zitadel (❌):** В документации **явно**: «does not support RFC 8707 and will reject requests containing the `resource` parameter». RFC 7591 (DCR) — feature request, не реализован. То есть **gateway-mcp для claude.ai/ChatGPT на Zitadel не запустить** без построения собственного DCR-прокси перед Zitadel — это ~2-3 недели работы Андрея + Паши + новые failure-points в OAuth-флоу. Hosted Login UI готов, admin Console — отличная, но это не закрывает блокер MCP. **Это ❌ по conjunctive screening: одна ось безусловно ломает выбор.**

### 3.5. С1 — Стабильность ✅ / ⚠️

**Ory (✅):** Hydra существует с 2015, Kratos — с 2019. SLA security: Critical ≤14 дней, High ≤30 дней. CVE в 2024-2025: единичные (например, бэкпорт CVE-2025-27144 в `go-jose`), без эксплуатируемых критических. Breaking changes между минорами редки. Релизный цикл — частые минорные, мажорный ~1-1.5 года.

**Zitadel (⚠️):** **В 2025 году опубликовано 13 CVE**, включая:
- CVE-2025-48936 (CVSS 8.1) — слабость password reset;
- CVE по неаутентифицированному SSRF через `x-zitadel-forward-host`;
- DOM-Based XSS в logout endpoint (v4);
- Brute-force lockout policy **отключён по умолчанию** и непоследовательно применялся в новых resource-API (требовался upgrade до v2.71.18 / v3.4.3 / v4.6.0);
- Username enumeration через прямой userIDs.

Релизный цикл: переход с 2-недельного на 3-месячный — но **breaking changes допустимы в alpha/beta**; параллельные ветки v2.x / v3.x / v4.x в 2025 (фрагментация). Поддержка мажора — ~6 мес после релиза следующего, что для on-prem GKE-деплоя — короткое окно для апгрейдов. ⚠️ — не блокирует, но требует disciplined patch-management.

### 3.6. С2 — Совместимость ✅ / ✅

**Ory (✅):** Out-of-the-box коннекторы к 15+ social-providers (Google, Apple, GitHub, Facebook, Microsoft, Discord, etc.). Apple — официальная инструкция с dynamic-secret из private key. Yandex — через generic OIDC. Passkeys / WebAuthn — FIDO2-стандарт, в core. Account linking — есть автоматический по verified email (с марта 2026 — auto-linking Apple), ручной flow с verification — стандартный.

**Zitadel (✅):** Google, GitHub, Apple, OIDC-generic. Passkeys / WebAuthn — FIDO2, документация подробная, Hosted Login UI поддерживает passkey autofill. SCIM, SAML. Account linking — поддерживается через external identity providers flow.

Оба ✅. По набору protocols/providers паритет. Yandex (актуально для Track A, но не Track B) — generic-OIDC в обоих.

### 3.7. Б — Безопасность ✅ / ⚠️

**Ory (✅):** SOC 2 Type II + ISO 27001 у Ory Network (cloud); для self-hosted — соответствующие компоненты под аудит-готовы. GDPR — европейская юрисдикция (Германия). Audit logs — events-API в Kratos + standard structured logs. MFA — TOTP, WebAuthn, SMS (через webhook), lookup secrets. Rate limiting / brute-force — встроен в Kratos hooks, конфигурируемый. Secret storage — Hydra использует encryption-at-rest для tokens (system secrets).

**Zitadel (⚠️):** SOC 2 Type II (январь 2026) + ISO 27001:2022. GDPR — швейцарская юрисдикция, decoupled от GDPR-территории, но GDPR-compliance заявлен. Audit logs — event-storing architecture даёт «неограниченный audit trail». MFA — TOTP, WebAuthn, OTP-email, SMS. Brute-force — **здесь проблема:** lockout policy была отключена по умолчанию вплоть до 2025; требует ручной активации «Password maximum attempts». Это нарушение **Security Gate B7.3** для PII-РП. ⚠️ — снимаемое настройкой, но добавляет ops-чеклист на каждом upgrade.

---

## 4. Conjunctive screening — результат

| Вариант | Количество ❌ | Прошёл экран? |
|---------|---------------|---------------|
| **Ory (Kratos + Hydra)** | 0 | ✅ Да |
| **Zitadel** | 1 (Г — отсутствие RFC 7591/8707 → ломает gateway-mcp) | ❌ Нет |

Согласно правилу архгейта (см. `.claude/skills/archgate/SKILL.md`), **один ❌ блокирует выбор**. Zitadel выпадает.

---

## 5. Стоимость переключения

| Сценарий | Часы Паши | Часы Андрея | Track A downtime |
|----------|-----------|-------------|------------------|
| **Остаёмся на Ory (рекомендация)** | ~16ч на новый EU-деплой Kratos+Hydra (Helm + secrets + DB-init); знания уже есть | ~8ч на конфиг gateway-mcp под новый endpoint | **0** (не трогаем) |
| **Переходим на Zitadel** | ~80-120ч (2-3 недели обучения + новый Helm + миграция концепций) | ~40-60ч (gateway-mcp требует кастомный DCR-прокси перед Zitadel, новый OAuth-флоу, повторная сертификация с claude.ai) | **0** (Track A остаётся на Ory) |
| **Δ переключения** | +64-104ч | +32-52ч | 0 |

Итого переключение стоит ~100-150 человеко-часов **только на восстановление функционального паритета** с текущим Ory-стеком. При этом ни одна из проблем Ory (4 микросервиса) не закрывается: ops-нагрузка на новый стек выше первое полугодие.

**Риск downtime в Track A:** 0 в обоих сценариях — Track A IdP не меняется по условию задачи.

---

## 6. Что НЕ решено профилем (вопросы для встречи)

ЭМОГССБ закрывает архитектурные оси, но эти вопросы остаются открытыми:

1. **Login-методы для MVP Track B.** Минимум: email+password + Google + Apple + passkey. Включать ли magic-link изначально или отложить?
2. **Account linking flow.** Если пользователь сначала зарегался по Google, потом нажал «Sign in with Apple» с тем же email — auto-link (Ory с марта 2026 умеет) или требовать явный шаг через настройки? Это UX-решение, не архитектурное.
3. **Tier-gate реализация (DP.ARCH.002).** В Ory tier-claims кладутся в `identity.metadata_public` и пробрасываются в JWT через Hydra → gateway-mcp валидирует. План: тот же подход, что в Track A. Подтвердить, что схема `tier`, `subscription_status`, `paid_until` совпадает в схемах identity Track A и Track B (миграция учётных записей маловероятна, но схема единая = легче переиспользовать gateway-логику).
4. **Migration claims-схемы.** Если в Track A какие-то traits Kratos уже мутировали (например, для VK-логина) — какие traits «обрезаются» для Track B (без VK, Yandex и т.д.)? Список с Пашей.
5. **GDPR data-residency.** Kratos EU = europe-west4 = Cloud SQL Postgres EU. Уточнить, что Helm-deploy Ory в europe-west4 GKE кластере + Cloud SQL EU + Cloud Logging EU bucket = всё в одной юрисдикции. Никаких US-логов.
6. **Ory Enterprise License (OEL) — нужна или нет.** OSS-сборки достаточны для MVP. OEL даёт enterprise-builds, SLA, дополнительные фичи (multi-region, SAML SP). Решение «на потом», когда будет >100 paying customers.
7. **Backup-стратегия identity-БД.** PITR Cloud SQL + еженедельный logical dump в GCS bucket. Согласовать RTO/RPO.

---

## 7. Рекомендация

**Решение: оставляем Ory (Kratos + Hydra) для Track B.** Keto и Oathkeeper не разворачиваем (как и в Track A) — оба микросервиса не задействованы, эта роль закрыта gateway-mcp на Cloudflare + JWT-валидацией в самих сервисах. Развёртывание: Helm-чарт `ory/kratos` + `ory/hydra` на GKE Standard europe-west4, Postgres = Cloud SQL EU, secrets через GCP Secret Manager.

**Action items для встречи 24 мая:**
- (Паша) Подготовить Helm values.yaml для EU-инстансов Kratos + Hydra, оценка ~4ч.
- (Андрей) Сверить env-переменные gateway-mcp под новый `ORY_URL`, schema совместима 1:1.
- (Тсерен) Зафиксировать ADR `ADR-NNN-track-b-idp-ory.md` в `C.IT-Platform/C2.IT-Platform/C2.2.Architecture/` со ссылкой на этот документ; статус-переход draft → review → active по итогам встречи.

**Alternatives — при каком условии пересмотреть:**

| Условие пересмотра | Когда проверять |
|---|---|
| Zitadel реализовал RFC 7591 + RFC 8707 (closed issue в zitadel/zitadel) | H2 2026, ежеквартально |
| Появился потребитель уровня enterprise, требующий per-tenant IdP-изоляции (B2B-SaaS multi-tenancy) | По мере появления крупных enterprise-клиентов |
| OEL стоимость превысила ~$15k/год, а в OSS-сборке Hydra нашёлся блокер | На годовом ревью lieence-costs |
| Серьёзный CVE в Ory Hydra/Kratos с CVSS ≥9.0 без быстрого фикса | Реактивно |

Если ни одно условие не выполнено — Ory остаётся на Track B бессрочно.

---

## Источники

- [Compare Ory vs ZITADEL — CIAM Vendors (ssojet.com)](https://ssojet.com/ciam-vendors/comparison/ory-vs-zitadel/)
- [Compared with Ory? · zitadel/zitadel · Discussion #4175](https://github.com/zitadel/zitadel/discussions/4175)
- [Securing MCP Servers with OAuth2: Ory Hydra + Claude Code + ChatGPT — getlarge.eu](https://getlarge.eu/blog/securing-mcp-servers-with-oauth2-ory-hydra-claude-code-chatgpt/)
- [Technical Deconstruction of MCP Authorization (kane.mx) — про отсутствие RFC 8707 в Zitadel](https://kane.mx/posts/2025/mcp-authorization-oauth-rfc-deep-dive/)
- [Zitadel CVE list (cvedetails.com)](https://www.cvedetails.com/vulnerability-list/vendor_id-28200/Zitadel.html)
- [ORY Hydra CVE list (cvedetails.com)](https://www.cvedetails.com/product/80066/ORY-Hydra.html?vendor_id=22691)
- [ZITADEL Production Setup (zitadel.com)](https://zitadel.com/docs/self-hosting/manage/production)
- [Ory Scalability (ory.com)](https://www.ory.com/docs/self-hosted/operations/scalability)
- [Ory Hydra resource limits — Discussion #3181](https://github.com/ory/hydra/discussions/3181)
- [ORY Hydra GitHub — упоминание OpenAI как production user](https://github.com/ory/hydra)
- [Ory Kratos Apple sign-in docs](https://www.ory.com/docs/kratos/social-signin/apple)
- [Zitadel Passkeys & WebAuthn docs](https://zitadel.com/docs/concepts/features/passkeys)
- [Zitadel GDPR](https://zitadel.com/gdpr)
- [Zitadel Brute-Force advisory (GHSA-xrw9-r35x-x878)](https://github.com/zitadel/zitadel/security/advisories/GHSA-xrw9-r35x-x878)
- [Zitadel Release Cycle](https://zitadel.com/docs/product/release-cycle)
- [Zitadel license change Apache → AGPL (blog)](https://zitadel.com/blog/open-source-in-the-ai-era)
- [ory/hydra issue #1616 — DCR support](https://github.com/ory/hydra/issues/1616)
