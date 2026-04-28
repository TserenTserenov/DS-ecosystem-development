---
type: architect-agenda
title: "ИТ-встречи с архитектором — повестка и итоги"
status: active
created: 2026-04-01
updated: 2026-04-28
depends_on: WP-73, WP-138, WP-228, WP-244, WP-250, WP-253, WP-258, WP-262, WP-265, WP-266, WP-268, WP-269, WP-270, WP-275, WP-276
source: встречи 1–12 (29 мар → 28 апр)
---

# ИТ-встречи с архитектором — повестка и решения

<details>
<summary><b>История встреч 1–12 (архив)</b></summary>

> **Встречи 1–5** закрыли: Блок А+Б+В, Keto-модель, Gateway, knowledge base, identity (ory_id), мягкое удаление, ЦД↔LMS, разделение Россия/мир, CRM = отдельный сервис.
> **Встреча 6 (12 апр):** kid="" распутан, gateway-mcp уточнён. Принцип «платформа Андрея ↔ инфра Паши».
> **Встреча 7 (13 апр):** двухшаговая MCP-безопасность (SET LOCAL + JWKS). Neon → одна `platform`. `subscription_grants` DONE.
> **Встреча 8 (14 апр):** kid="" исправлен. WP-212 B4.22–24 DONE. Вариант E (ADR-IWE-012) — каждый MCP верифицирует JWT сам.
> **Встреча 9 (19 апр, оперативка):** Q2-режим (поддерживаем MVP). WP-215 заморожен. ER-диаграммы только физ.объекты. Public status page = SaaS.
> **Встреча 10 (21 апр, 14:00–17:00):** обсуждены А выжимка / Б ER 9 БД / В безопасность B7.3-5 / Г Keto. Утверждены **Р-MVP-Freeze** (Q2), **Р-ER-Guidelines** (Chen, физ.объекты, размещение в Pack), **Р-Audit-Process** перенесено на после MVP. Утренняя оперативка → 12 правок DP.ARCH.004 v2.
> **Встреча 11 (26 апр, оперативка + TG-диалог 15:03–15:46):**
> - Обсуждены 4 темы: А WP-268 cut-over vs dual-write, Б DP.ARCH.004 v2.4 mutual read-only LMS↔Neon, В ADR-IWE-014 граница L2/L3, Г2 Hetzner-сервер.
> - Утверждены: **Р-CutOver** (cut-over 3-5 дней вместо dual-write soak 14 дней — DROP 1 мая); **Р-MutualReadOnly** (pattern LMS↔Neon принят как рабочий, Bridge-2 операционный компонент на transition); **Р-OpenCore ADR-IWE-014** (двухуровневая open-core L2 платформа + L3 персональный IWE — каноничен для downstream WP-258/WP-262/WP-188).
> - **Hetzner-сервер (Г2):** Tseren грузит руками («Времянка с эвакуацией»); Андрей займётся NixOS+автодеплой «скоро».
> - **Открыто (отложение Q2):** B7.3 ревью безопасности Паша → после MVP 1 мая; B7.4 внешний human-аудит → Q3; Г Keto статус → после MVP.
>
> **Встреча 12 (28 апр, оперативка ИТ 08:57–09:17 МСК, ~20 мин):** transcript: `~/Documents/Zoom/2026-04-28 08.57.42 Оперативка ИТ/transcript.txt`.
> - **А1 (Ory клуб-адаптер):** Наталья подтвердила работу с её стороны вчера. Андрей сделал поддержку Ory-токенов в адаптере клуба (помимо API-ключа). Сегодня проверит → задеплоит на прод. Бот сможет переиспользовать адаптер вместо собственного API-ключа клуба (tseren сейчас ходит мимо адаптера). **Передача:** «как закончу с клубом, с адаптером — скину тебе».
> - **A1 (EU-инстанс Ory на Hetzner) — НЕ обсуждался** (выпал из повестки), оставляем open для встречи 13.
> - **Б1+Б5 (2-server architecture):** ✅ **Андрей сам предложил купить второй сервер за свой счёт** для своей платформы автоматизации, чтобы «не на твоих вещах экспериментировать». Подключит Tseren когда будет готовность. Tseren продолжает «Времянку» на Сервере 1.
> - **Б4 (embedding service):** ⚠️ **Отвергнут Андреем как daemon-сервис.** Новый паттерн: индексация = GitHub Actions workflow (триггер по коммиту), либо на GitHub-серверах, либо self-hosted GHA runner на Сервере 1. Влечёт правки в WP-138 + WP-276.
> - **Б2 (NixOS таймлайн «скоро»):** не уточнён, но получено объяснение — это часть платформы автоматизации, упрощающий язык поверх NixOS пока не сделан. Без него NixOS «сложновато».
> - **B+Г+Д+Е** (status-sync по WP-268/WP-253/Better Stack/security/Aisystant MCP rebrand): не дошли — встреча была короткая (~20 мин). Перенос на встречу 13 (когда Андрей закончит с адаптером клуба).
> - **Инцидент 27 апр:** Tseren упомянул, вчера упал digital-twin-mcp; Better Stack отработал штатно (TG-уведомление). Композитный SLA за месяц 98.5% (вместо 100%). Зафиксировано в incident-log как follow-up для root-cause.

</details>

---

## Повестка встречи 13 (TBD — после задеплоя адаптера клуба Андреем)

<details open>
<summary><b>Встреча 13 — продолжение неотвеченных вопросов встречи 12 + status-sync MVP</b></summary>

> **Триггер:** «Как закончу с клубом, с адаптером — скину тебе» (Андрей, 28 апр). Ориентировочно конец W18 / начало W19 после деплоя адаптера на прод и проверки Tseren.
>
> **Что произошло за 2 дня (27–28 апр) — крупные сдвиги:**
> - ✅ **WP-269 read-path migration DONE 27 апр** — 3 readers + 4 lazy pools + retry-loop B4 → pilot → prod (FORCE_PROD=1), smoke @aist_me_bot PASS. Persona reader hotfix `COALESCE(canonical, alias)` для silent terminology drift `aisystant_suser_id` vs `aisystant_id`. 3 hold-outs G1/G2/G3 (FSM state, Q&A history, GitHub connections) → backlog Strategy Session W19.
> - ✅ **WP-270 multi-domain projection-worker DONE 27 апр** — ArchGate v4 PASS Вариант Б (per-domain cursor) + Ф1 implement. 9 миграций 022-103 на prod Neon + Railway worker `multi-domain-projection-worker` LIVE. 4 cursors persona/subscription/indicators/learning + UPSERT idempotency + `_when` поля + `_lookups` async resolve + PII redact + FORBIDDEN_FIELDS whitelist. Tests 24/24 PASS. **Worker задеплоен в проекте `attractive-optimism` (НЕ peaceful-vision — Railway "+ New" pitfall, см. feedback).** Sequential throughput ceiling ~50-60 ev/min на Neon-pooled.
> - ✅ **WP-275 LIVE 27 апр** — 9 Better Uptime monitors (keyword-check + 3 регионов + SSL/domain expiry) + AIST Bot heartbeat + CF Worker Route `twin.aisystant.com/*` → digital-twin-mcp (commit `45d3acf` + `[[routes]]` в wrangler.toml). Найдено: **event-gateway 503 (DB auth `neondb_owner`)** — отдельный РП Паше. Новый HD: **CF Worker Route ≠ Worker Custom Domain** (OAuth-токен wrangler без `dns:write` → use Route).
> - ✅ **WP-273 DONE 27 апр** — Архитектура интеграционных контрактов IWE (FMT-exocortex-template) — 8 релизов 0.28.11→0.29.7, 19 пунктов R4/R5/R6 закрыто, smoke 11/11 + validator 8/8 + sub-agent STABLE. Паттерн: «proactive audit нашёл 5 классов проблем до Round 6».
> - ✅ **WP-274 DONE 27 апр** — Quantum-like линза FPF C.26* интегрирована (HD #50 + DP.SOTA.020 + DP.METHOD.050). Линза для ArchGate / observability / диагностики, активируется после исчерпания классики.
> - ✅ **WP-272 Ф4 DONE 27 апр** — 18 правил агента расписаны по FPF A.7 (Object/Description/Carrier hint), audit fix (cycle-detection DFS), weekly evolution routine. Backlog 17→0.
> - ✅ **Strategy Session W18 + Month-Close апреля (27 апр):** R-таблица: апрель закрыт (R1 Ory ✅, R2 архитектура ✅ ключевые, R6 Память.Derived ✅ через WP-253) → май R1-R5; ТОС-мая «безопасность + стабильность генерации руководства»; Strategy.md restructure.

---

### А. Ory — продолжение

| # | Вопрос | Контекст |
|---|--------|----------|
| **A1** | Адаптер клуба с Ory — задеплоен на прод? Tseren проверил с своей стороны? Бот переключён на адаптер вместо своего API-ключа? | Передача Андрея 28 апр: «как закончу с клубом, с адаптером — скину тебе». Деплой ожидался 28 апр после проверки. |
| **A1bis** | План EU-инстанса Ory на Hetzner — выпал из встречи 12. Поднимаем на Сервере 1 в W19+ или ждём NixOS-платформу + Сервер 2 Андрея? | Открытое с TG 26 апр + повестка 12. |
| **A4** | После cut-over 1 мая ревизия двухшаговой MCP-безопасности (ADR-IWE-010 + ADR-IWE-012)? JWT-верификация работает корректно на 6 БД новой архитектуры? | Smoke @aist_me_bot ✅ 27 апр; нужно подтверждение независимости JWKS-верификации. |
| **A5** | Aisystant MCP rebrand prod re-deploy — stale 17+ дней (5 коммитов). Деплоим? | WP-259 Ф5, smoke-test ~5 мин. Display-identity-only, machine identity не меняем. |

### Б. WP-268 cut-over итоги (после 1 мая)

| # | Вопрос | Контекст |
|---|--------|----------|
| **Б1** | DROP digitaltwin/neondb/directus 1 мая — прошёл штатно? | Production cut-over deploy 29 апр, soak 30 апр, DROP 1 мая. |
| **Б2** | Sequential worker throughput ceiling 50-60 ev/min (WP-270) — реальная нагрузка core-team прогона 30 апр и пилота 11-15 мая? | Триггер Ф3 scaling = когорта 50+ пользователей. |
| **Б3** | DROP остальных legacy БД (aist_bot + platform) после exclusive tables ETL — таймлайн 16-17 мая подтверждён? | Зависит от Bridge-2 cleanup. |

### В. WP-253 Ф9.5 итоги (после 30 апр core-team прогона)

| # | Вопрос | Контекст |
|---|--------|----------|
| **В1** | TG core-team прогон 30 апр (5 чел, инструкция /personal-guide-start) — feedback? Регрессии? | 5 чел: Tseren, Дима, Андрей, Паша, Ильшат. |
| **В2** | WP-244 Ф3b internal_metrics writer LIVE (блокер Ф9.6 reliability gate 4-6 мая) — готов? | Сегодня делается. |

### Г. Инцидент digital-twin-mcp 27 апр (новое из встречи 12)

| # | Вопрос | Контекст |
|---|--------|----------|
| **Г1** | Root-cause падения digital-twin-mcp 27 апр (композитный SLA 98.5% за месяц вместо 100%) — известен? | Better Stack отработал штатно (TG-уведомление пришло). Нужен post-mortem или это было известное событие (например, deploy-related)? |
| **Г2** | Нужен ли мини-РП на root-cause или закрываем как «известный transient»? | Решение зависит от ответа Г1. |

### Д. Подтверждение отложений Q2 (от встречи 11)

| Вопрос | Текущий статус | Подтверждение нужно |
|--------|----------------|----------------------|
| B7.3 ревью безопасности (Паша) | отложено после MVP 1 мая | Да |
| B7.4 внешний human-аудит | Q3 2026 | Без изменений |
| Г Keto статус | подвисло, после MVP | Да |
| Aisystant MCP rebrand | stale 17 дней | См. A5 |

### Е. WP-276 (новый зонтичный РП от 28 апр) — представление Андрею

| # | Что показать | Цель |
|---|--------------|------|
| **Е1** | Двухуровневая структура карты внешних провайдеров (Pack: 12 групп + DS: экземпляры). Drift-детектор как расширение паттерна WP-263. | Получить согласие на структуру и быть co-author |
| **Е2** | Поправка по embedding service — теперь через GHA workflow по коммиту (паттерн Андрея). | Подтвердить корректное понимание |
| **Е3** | Discourse / Sentry / GCP / Vercel — какие реально используются? | Закрыть слепые пятна перед Ф2 |

</details>

---

<details>
<summary><b>Итоги встреч (хронология решений)</b></summary>

| # | Вопрос | Решение | Дата |
|---|--------|---------|------|
| **Россия/мир** | Разделение инфраструктуры | ✅ Полное разделение финансов по юрлицам. → WP-215 (заморожен 19 апр) | 9 апр |
| **CRM** | Отдельный сервис | ✅ Выделяем отдельный сервис учёта оплат | 9 апр |
| **Neon** | Одна база | ✅ `platform` со схемами (12-13 апр). Целевое: 9→**12 БД** v2.3 (26 апр) | 9 / 13 / 19 / 26 апр |
| **Сервер** | Activity Hub, Langfuse | ⏸️ Заморожено на Q2 | 9 апр |
| DE-34 + Р4 | Identity: ory_id | ✅ Только ory_id. | 7 апр |
| DE-36 | Клуб → Ory | ✅ Паша передоплывает с нуля | 12 апр |
| ЦД ↔ LMS | Интеграция | ✅ Подтягивать при первом входе | 7 апр |
| Git | Хранилище | ✅ Git = primary | 7 апр |
| Удаление | Мягкое | ✅ Флаг «заархивировано» | 7 апр |
| Gateway | Прозрачный прокси | ✅ Не фильтрует, не нормализует | 5 апр |
| Knowledge base | Разделение | ✅ Личная/проектная/публичная | 5 апр |
| Gate T2+ | Keto permissions | ✅ Permissions → роли | 5 апр |
| Ory URL | Keto URL | ⏳ Подвисло, обсуждать после MVP | 5 апр |
| GDPR | Трансграничная передача | ⏸️ Отложено | 5 апр |
| **kid="" природа** | JWT kid в Ory токене | ✅ Распутано 12 апр; Fixed 14 апр | 12-14 апр |
| **Архитектура MCP-безопасности** | RLS + JWT двухшаговая | ✅ ADR-IWE-010 | 13 апр |
| **Neon консолидация** | Одна база `platform` | ✅ ADR-IWE-009 (WP-232) | 13 апр |
| **Реестр подписок** | subscription_grants | ✅ ADR-IWE-011. 2740/771 активных | 13 апр |
| **Вариант E** | MCP independent JWT verification | ✅ ADR-IWE-012 | 14 апр |
| **DB #8 health** | Наблюдаемость изолирована | ✅ ADR-IWE-013 | 15 апр |
| **9 БД** | Целевая архитектура (WP-228) | ✅ ArchGate. Эволюция → 12 БД v2.3 (26 апр) | 19 апр |
| **Q2 freeze WP-215** | Массовый vs нишевый продукт | ✅ Гипотеза: подписка = массовый продукт через адаптивную персонализацию | 19 апр |
| **ER-guidelines** | Только физ.объекты, Chen notation | ✅ HD + DP.METHOD.040 | 19 / 21 апр |
| **Public status page** | Готовый SaaS | ✅ Better Uptime LIVE 24 апр | 19 / 24 апр |
| **WP-244 observability** | LIVE end-to-end | ✅ status.aisystant.com + 11 monitors + /status в боте | 24 апр |
| **WP-253 Ф9** | Event-gateway + projection-worker | ✅ LIVE, 4 gates PASS, узкое место MVP снято | 24-25 апр |
| **ADR-IWE-014** | Граница L2/L3 open-core | ✅ Accepted (Tseren) | 26 апр |
| **DP.ARCH.004 v2.4** | Mutual read-only LMS↔Neon | ✅ Pattern добавлен | 26 апр |
| **DP.ARCH.001 принцип 26** | Read-only mode для скиллов с side-effects | ✅ Принято | 26 апр |
| **WP-268 6 БД** | Переезд за день | ✅ DONE 26 апр | 26 апр |
| **WP-268 cut-over vs dual-write** | Стратегия перехода | ✅ Cut-over accepted (3-5 дней, DROP 1 мая). Day 1+2 выполнен 27-28 апр, prod deploy 29 апр | 26 апр |

</details>

<details>
<summary><b>Бэклог (не на ближайшую встречу)</b></summary>

**Ждут внешних условий:**
- **Юрконсультация Q9/Q11.** Заморожена вместе с WP-215.
- **Перечень данных для RU↔EU репликации** — заморожен вместе с WP-215.

**Архитектурные вопросы на отдельную встречу (Q3+):**
- **Encryption at rest:** pgcrypto / app-level / Vault — после MVP.
- **Inter-service auth:** стандартизация вызовов между сервисами — не блокер.
- **Сертификации SOC 2 / ISO 27001** — после подтверждения массового продукта.
- **Matcher каналов** (Telegram + email + Ory) — нет owner, нет срока.
- **РФ-хостинг выбор** (Hetzner Russia vs VK Cloud vs Selectel) — Q12, заморожен.
- **Unit economics по тирам** — C4, Q3+.
- **Web App Vue/Nuxt** (ADR-001) — после подтверждения гипотезы.

</details>
