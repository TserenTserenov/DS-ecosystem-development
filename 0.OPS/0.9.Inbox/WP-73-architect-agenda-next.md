---
type: architect-agenda
title: "ИТ-встречи с архитектором — повестка и итоги"
status: active
created: 2026-04-01
updated: 2026-04-28
depends_on: WP-73, WP-228, WP-244, WP-250, WP-253, WP-258, WP-262, WP-265, WP-266, WP-268, WP-269, WP-270, WP-275
source: встречи 1–11 (29 мар → 26 апр)
---

# ИТ-встречи с архитектором — повестка и решения

<details>
<summary><b>История встреч 1–11 (архив)</b></summary>

> **Встречи 1–5** закрыли: Блок А+Б+В, Keto-модель, Gateway, knowledge base, identity (ory_id), мягкое удаление, ЦД↔LMS, разделение Россия/мир, CRM = отдельный сервис.
> **Встреча 6 (12 апр):** kid="" распутан, gateway-mcp уточнён. Принцип «платформа Андрея ↔ инфра Паши».
> **Встреча 7 (13 апр):** двухшаговая MCP-безопасность (SET LOCAL + JWKS). Neon → одна `platform`. `subscription_grants` DONE.
> **Встреча 8 (14 апр):** kid="" исправлен. WP-212 B4.22–24 DONE. Вариант E (ADR-IWE-012) — каждый MCP верифицирует JWT сам.
> **Встреча 9 (19 апр, оперативка):** Q2-режим (поддерживаем MVP). WP-215 заморожен. ER-диаграммы только физ.объекты. Public status page = SaaS.
> **Встреча 10 (21 апр, 14:00–17:00):** обсуждены А выжимка / Б ER 9 БД / В безопасность B7.3-5 / Г Keto. Утверждены **Р-MVP-Freeze** (Q2), **Р-ER-Guidelines** (Chen, физ.объекты, размещение в Pack), **Р-Audit-Process** перенесено на после MVP. Утренняя оперативка → 12 правок DP.ARCH.004 v2.
> **Встреча 11 (26 апр, оперативка + TG-диалог 15:03–15:46):**
> - Обсуждены 4 темы: А WP-268 cut-over vs dual-write, Б DP.ARCH.004 v2.4 mutual read-only LMS↔Neon, В ADR-IWE-014 граница L2/L3, Г2 Hetzner-сервер.
> - Утверждены: **Р-CutOver** (cut-over 3-5 дней вместо dual-write soak 14 дней — DROP 1 мая); **Р-MutualReadOnly** (pattern LMS↔Neon принят как рабочий, Bridge-2 операционный компонент на transition); **Р-OpenCore ADR-IWE-014** (двухуровневая open-core L2 платформа + L3 персональный IWE — каноничен для downstream WP-258/WP-262/WP-188).
> - **Hetzner-сервер (Г2):** Tseren грузит руками («Времянка с эвакуацией» — pre-prod Postgres + B2 backup + embedding service); Андрей займётся NixOS+автодеплой «скоро» (таймлайн уточняется на встрече 12). Bridge-2/rewards-worker НЕ переносим (state risk).
> - **Открыто (отложение Q2):** B7.3 ревью безопасности Паша → после MVP 1 мая; B7.4 внешний human-аудит → Q3; Г Keto статус → после MVP. Подтверждается на встрече 12.

</details>

---

## Повестка встречи 12 (28 апр, вторник, 14:00–15:00 МСК)

<details open>
<summary><b>Встреча 12 — статус с 26 апр + ORY + загрузка сервера</b></summary>

> **Главные вопросы:** (1) **ORY** — состояние и план EU-инстанса после покупки Hetzner; (2) **Загрузка Hetzner-сервера** — что Tseren грузит сегодня вечером, координация с NixOS-планом Андрея; (3) WP-268 Phase 2 cut-over статус (Day 2 сегодня, deploy 29 апр, DROP 1 мая); (4) WP-253 Ф9.5 prep к 30 апр; (5) FYI по WP-244/WP-269/WP-270/WP-275/WP-273.
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

### А. ORY — статус и план EU-инстанса (главный вопрос 1)

> **Контекст:** ORY self-hosted в РФ (Hetzner Helsinki) утверждён 28 мар; гейтвей gateway-mcp Ory OAuth ✅ done 5 апр; kid="" fixed 14 апр; B4.21 Ory JWT глобально DONE 10 апр; subscription_grants как единый источник права ✅ done 13 апр (ADR-IWE-011); Вариант E (каждый MCP верифицирует JWKS сам) ✅ done 14 апр (ADR-IWE-012); **Hetzner-сервер куплен 1 апр (WP-70 DONE), $53.43/мес, Helsinki**.

**Что просим от Андрея на встрече 12:**

| # | Вопрос | Контекст |
|---|--------|----------|
| **A1** | План EU-инстанса Ory: поднимаем на Hetzner сейчас (Tseren в «Времянке») или ждём NixOS-платформу? | Открытое с TG-диалога 26 апр 15:46 — таймлайн «скоро». Если NixOS через 2-3 недели — ставить ORY EU вручную сегодня вечером? |
| **A2** | Q12 — РФ-хостинг для self-hosted ORY (заморожен): после Hetzner Finland что считаем РФ-инстансом? Hetzner Russia / VK Cloud / Selectel — кто принимает решение и когда? | Заморожен до MVP, но WP-215 Q2 freeze продлён — хотим подтвердить, что РФ-хостинг откладываем до Q3 |
| **A3** | GDPR / репликация RU↔EU (Б8) — после Q2 freeze WP-215 что с этим вопросом? Юрконсультация Q9/Q11 заморожена — есть ли сигналы менять статус? | Олег: «европейцы спросят про русские данные». Open сейчас не блокирует MVP, но ставит лимит на iEU-маркетинг |
| **A4** | После cut-over 1 мая нужен ли ревизия двухшаговой MCP-безопасности (ADR-IWE-010 + ADR-IWE-012)? Все 6 БД на prod Neon новой архитектуры — JWT-верификация работает корректно? | Smoke smoke @aist_me_bot ✅ 27 апр; нужно подтверждение, что кросс-БД RLS из персональных данных не сломан после миграции |
| **A5** | **Aisystant MCP rebrand** — production stale 14 дней (5 коммитов). Re-deploy сегодня/завтра? Какой риск (display-identity-only, machine identity не меняем)? | WP-259 Ф5; smoke-test post-deploy ~5 мин |

**Цель:** до конца встречи знать (1) поднимать ли ORY EU сегодня вечером в «Времянке», (2) что отложено до Q3, (3) что нужно re-verify после cut-over.

📄 [WP-138 — Autonomous IWE cloud runtime](../../../DS-my-strategy/inbox/WP-138-autonomous-iwe-cloud-runtime.md) — context Hetzner+NixOS

---

### Б. Загрузка Hetzner-сервера — план «Времянка с эвакуацией» (главный вопрос 2)

> **Контекст:** Hetzner Intel Xeon E3-1275V6 / 64GB DDR4 / 2× NVMe 512GB / Finland HEL1-DC2, $53.43/мес. **TG-диалог 26 апр 15:03–15:46:** Андрей: NixOS+автодеплой «скоро» (как недостающий компонент платформы автоматизации); Tseren: «могу сам сейчас этот сервер загрузить руками» — ✅ Андрей подтвердил.
>
> **План Tseren на сегодня вечер (4-6h):** «Времянка с эвакуацией» — Ф0 руками: pre-prod Postgres + B2 backup + embedding service. Всё восстанавливается из git за 1-2h после переустановки.

**Что просим от Андрея на встрече 12:**

| # | Вопрос | Контекст |
|---|--------|----------|
| **Б1** | Уточнение таймлайна «скоро» — недели / месяц / квартал? От этого зависит объём вложений в текущую «Времянку». | Если 2-3 недели — ставить минимум (только pre-prod Postgres). Если 1-2 месяца — добавлять embedding service и пробовать как ORY EU host. |
| **Б2** | Список того, что Tseren грузит сегодня — корректно? Есть ли что-то, что НЕ ставить руками (state-критичное)? Bridge-2/rewards-worker/multi-domain-projection-worker — НЕ переносим (state risk + Railway-managed). | Tseren: pre-prod Postgres + B2 backup + embedding service. Возможно ORY EU (см. A1). |
| **Б3** | Разделение ownership: что Tseren поддерживает «вручную» vs Андрей берёт на NixOS? Должен ли Tseren документировать установки в `configuration.nix`-friendly формате (списком пакетов/сервисов)? | Чтобы потом легко «переустановить ОС → восстановить из git за 1-2h» в NixOS-формате. |
| **Б4** | Embedding service — какой вариант (sentence-transformers через FastAPI / Ollama / Hugging Face TEI)? Это будет общий сервис для knowledge-mcp / personal-knowledge-mcp / digital-twin-mcp / future ORY EU? | Сейчас knowledge-mcp использует pgvector через Neon — embedding генерится в Worker / в скриптах. Возможно вынести в выделенный сервис. |
| **Б5** | После эвакуации — переезд в новый сервер или переиспользование текущего? «Можем потом взять новый и перенести туда всё» (Андрей 26 апр) — это решение или открыто? | Стоимость второго сервера $53/мес — приемлемо. Но если можно reuse — экономия. |

**Цель:** до конца встречи иметь чёткий список «что поставить сегодня вечером» + критерий «что точно не ставить» + понимание таймлайна NixOS-эвакуации.

📄 [WP-138 — план Ф0-Ф5](../../../DS-my-strategy/inbox/WP-138-autonomous-iwe-cloud-runtime.md)

---

### В. WP-268 Phase 2 cut-over — статус Day 2 (FYI + sync)

> **Контекст:** решение 26 апр (Tseren) — cut-over (3-5 дней) вместо dual-write soak (14 дней). 26 апр (вс) 6 БД переехали за день; 27 апр Day 1 — WP-269+WP-270 done; 28 апр Day 2 — bot rewrite Phase B + parity verify + 24h pilot soak; 29 апр — production cut-over deploy + 5 core-team; 30 апр — production soak + DROP decision; 1 мая — DROP digitaltwin/neondb/directus.

**Status sync (без вопросов на утверждение):**

- **Сегодня (28 апр):** bot rewrite Phase B (events.py:log_event central → routing на 5 новых БД) + parity verify count'ы legacy vs new + 24h pilot soak.
- **Завтра (29 апр):** production cut-over deploy, прогон с 5 core-team (Tseren, Дима, Андрей, Паша, Ильшат?).
- **Чт (30 апр):** production soak 24h + decision DROP.
- **Пт (1 мая):** DROP digitaltwin + neondb + directus (aist_bot и platform — после exclusive tables ETL, ETA 16-17 мая).
- **B7.3 PII payment_credentials** payment-registry миграция — отложена до W18+ (рамка Q2-режима).

**Открытый возможный риск:** sequential worker throughput ceiling ~50-60 ev/min (WP-270). Для 5 core-team волонтёров пилот W19 — нет блокера, но при 50+ когорте Ф3 нужен сразу.

📄 [WP-268 cut-over strategy](../../../DS-my-strategy/inbox/WP-268-cutover-strategy.md) · [WP-270 apply checklist](../../../DS-my-strategy/inbox/WP-270-apply-checklist.md)

---

### Г. WP-253 Ф9.5 finalize prep к 30 апр (FYI)

> **Контекст:** TG core-team прогон 30 апр (5 человек, инструкция /personal-guide-start готова). Деплой-runbook + smoke-tests финал + observability checklist.

**Status sync (без вопросов на утверждение):**

- **Сегодня (28 апр):** deploy-runbook commit + TG core-team message ready.
- **Завтра (29 апр):** load-test runner + failure-mode runner подготовка.
- **Чт (30 апр):** TG core-team прогон + сбор feedback + WP-244 Ф3b internal_metrics writer LIVE (блокер Ф9.6 reliability gate 4-6 мая).

📄 [WP-253 Ф9.5 deploy-runbook](../../../DS-ecosystem-development/0.OPS/0.9.Inbox/WP-253-F9.5-deploy-runbook.md) (создаётся сегодня)

---

### Д. Краткий статус остальных РП (FYI, без вопросов)

- ✅ **WP-269 read-path migration DONE 27 апр**: 3 readers переключены на новую архитектуру, smoke pilot+prod PASS. Hold-outs G1/G2/G3 backlog.
- ✅ **WP-270 projection-worker DONE 27 апр**: ArchGate v4 + Ф1 implement + apply LIVE на prod.
- ✅ **WP-275 LIVE 27 апр**: 9 Better Uptime monitors + Twin route fix.
- ✅ **WP-273 DONE 27 апр**: 8 релизов FMT 0.28.11→0.29.7.
- ✅ **WP-274 DONE 27 апр**: quantum-like FPF C.26* интегрирована.
- ✅ **WP-272 Ф4 DONE 27 апр**: 18 правил FPF A.7. Ф5 spawn (runtime activation 6.5h).
- 🟡 **WP-187 Ф-L.1 + Ф-K.2 (Паша параллельно сегодня)**: MCP tools + auto-init, дедлайн 30 апр.
- 🟡 **WP-244 Ф3b internal_metrics writer (сегодня, 1.5h)**: блокер WP-253 Ф9.6 reliability gate.
- 🟡 **WP-250 Ф-F.2 done утром / Ф-F.3 синх с Пашей старт сегодня**: публикация ADR L2/L3 1 мая.
- 🟡 **WP-262 «Бот тонкий клиент»**: активация Q2-Q3 после 1 мая.
- 🟡 **WP-258 Plugin API L2**: активация после ADR-IWE-014 (accepted 26 апр).
- 🟡 **Aisystant MCP rebrand prod re-deploy**: stale 14 дней (см. A5).

---

### Е. Открытые с встречи 11 (статус)

| Вопрос | Статус 28 апр | Действие |
|--------|----------------|----------|
| **B7.3 ревью безопасности (Паша)** | отложено до после MVP 1 мая | подтвердить отложение (Q2-режим) |
| **B7.4 внешний human-аудит** | Q3 2026 | без изменений |
| **B7.5 Security Gate в CLAUDE.md** | RTM batch Евгения 10/10 ✅ — отдельный Gate чек-лист пока не требуется | подтвердить — текущий ArchGate достаточен |
| **Г. Keto статус** | подвисло, обсуждать после MVP | подтвердить отложение |
| **Р-CutOver** | ✅ выполнено по плану (Day 1+2) | confirm — продолжаем по графику |
| **Р-MutualReadOnly** | ✅ pattern LIVE (DP.ARCH.004 v2.4) | confirm — без изменений |
| **Р-OpenCore ADR-IWE-014** | ✅ accepted 26 апр | confirm — публикация в составе WP-250 Ф-F.3 (1 мая) |

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
