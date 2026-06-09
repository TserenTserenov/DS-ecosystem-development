---
type: doc
status: active
created: 2026-05-22
updated: 2026-06-09
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
  - WP-285-services-inventory.md
  - WP-285-track-b-plan.md
  - WP-285-ory-vs-zitadel-emogssb.md
tags:
  - track-b
  - decisions-registry
  - wp-285
---

# WP-285: Реестр принятых решений по Track B

> **Назначение:** единая точка истины по всем архитектурным и операционным решениям Track B (мировая платформа Aisystant). Источник для встречи 24 мая и последующих итераций.
>
> **Связанные документы:**
> - [WP-285-services-inventory.md](WP-285-services-inventory.md) — реестр сервисов Track A → Track B (16 сервисов + 15 БД)
> - [WP-285-track-b-plan.md](WP-285-track-b-plan.md) — детальный план реализации (Фаза 0-6, дедлайн MVP — конец июня)
> - [WP-285-ory-vs-zitadel-emogssb.md](WP-285-ory-vs-zitadel-emogssb.md) — ArchGate IdP (Ory vs Zitadel, профиль ЭМОГССБ)
>
> **Конвенция ID:** `Р-<дата>-<N>`, где дата — день решения. `Р-инв-N` — решения, зафиксированные в инвентаре (вне явных встреч). Источник всегда указан явно.

---

## А. Инфраструктура

| ID | Решение | Источник |
|---|---|---|
| Р-14-1 | **GKE Standard** (europe-west4), не Autopilot — 0.5 vCPU floor дорог при малой нагрузке | Встреча 14, 7 мая |
| Р-14-2 | **Cloud SQL** (PostgreSQL, europe-west4) — $0 egress в тот же регион | Встреча 14, 7 мая |
| Р-14-3 | **GCP Artifact Registry** (europe-west4) как container registry | Track B plan §1.6 |
| Р-14-4 | **CI/CD:** GitHub Actions → Artifact Registry → Werf → GKE; PR merge = auto-deploy | Track B plan §1.11 |
| Р-14-5 | **Werf** для деплоя — разработчик пишет минимальный манифест, DevOps добавляет инфра-специфику | Встреча 14, 7 мая |
| Р-14-6 | **Terraform Cloud** для IaC в отдельном репо | Встреча 14, 7 мая |
| Р-14-7 | **Отдельная GitHub-организация** для Track B — Паша создаёт, форкает нужные репо | Встреча 14, 7 мая |

## Б. Разделение треков

| ID | Решение | Источник |
|---|---|---|
| Р-15-1 | **Ильшат принимает Track A**, Тсерен переключается на Track B (WP-281 Ф4, дедлайн 1 сентября) | Оперативка 14 мая |
| Р-22-2 | **aisystant.com — только мир.** Для Track A постепенный переезд на aisystant.ru — отдельный РП с миграционным планом (redirect aisystant.com → aisystant.ru на ~6 мес + уведомление пользователей) | Переписка с Андреем, 22 мая |
| Р-инв-1 | Track A (Россия) работает как есть — ничего не трогаем (Neon + Railway + VK Cloud Ory + YooKassa) | Inventory §1-§4 |
| Р-инв-2 | Track B стартует **пустым** — данные не мигрируются. Пользователи Track A переходят через явный экспорт/импорт (Track B plan Фаза 6) | Inventory §3 |
| Р-инв-3 | **15 БД в Cloud SQL** — без metabase (отложен до накопления аналитических данных, см. inventory §7) | DP.SC.131, 15 мая |

## В. Сервисы

| ID | Решение | Источник |
|---|---|---|
| Р-15-5 | **Dockerfile ✓ для 4 из 6 Python-сервисов.** Открытые: payment-registry (TBD deployment model), google-drive-mcp (нужен Dockerfile под GKE) — решить до Фазы 3.3 | Оперативка 14 мая |
| Р-15-6 | **12-factor compliance = prerequisite.** WP-307 закрыт 13 мая; риски миграции снижены | Оперативка 14 мая |
| Р-22-1 | **CF Workers остаются на Cloudflare.** Кандидаты на перенос в GKE — только `event-gateway` (транзакционность к Cloud SQL journal) и `payment-receiver` (cluster-internal к payment-registry); финальное решение по этим двум — на встрече 24 мая | Переписка с Андреем, 22 мая |
| Р-инв-4 | `bridge-2-events-poller` **не переносим** — polling legacy LMS только Track A | Inventory §2 |
| Р-инв-5 | `rewards-projection-worker` **decommission'd** — функционал поглощён `multi-domain-projection-worker` | WP-311 Ф-Close, 17 мая |
| Р-инв-6 | **Не в scope Track B:** autonomous agents (A1-A6), profiler (P1), launchd-планировщик (T1), local gateway (L1), hetzner-backstage (X2), ssm2025 (X3) — остаются в инфре пилота/Track A | Inventory §7, WP-307 |

## Г. Платежи

| ID | Решение | Источник |
|---|---|---|
| Р-инв-7 | **Stripe только** на Track B (USD/EUR/...) — YooKassa не нужна | Inventory §4 |
| Р-22-7 | **Stripe-аккаунт юрисдикция:** обсудить на встрече 24 мая (ИП Тсерена / ООО / Foundation в Q3-Q4) — отложенное решение | Переписка с Андреем, 22 мая (open) |

## Д. Auth (IdP) и login-методы

| ID | Решение | Источник |
|---|---|---|
| Р-инв-8 | **Ory EU** разворачивается на GKE EU — отдельный инстанс от Track A (Kratos + Hydra на GKE, своя БД) | Track B plan §2.2-2.3 |
| Р-22-5 | **Ory остаётся** (Kratos + Hydra) для Track B. **Zitadel отклонён** — нет RFC 7591 (DCR) и RFC 8707 (Resource Indicators), ломает интеграцию gateway-mcp с claude.ai/ChatGPT. Conjunctive screening: Ory 0×❌, Zitadel 1×❌ | ArchGate ЭМОГССБ, 22 мая ([WP-285-ory-vs-zitadel-emogssb.md](WP-285-ory-vs-zitadel-emogssb.md)) |
| Р-22-5а | **Keto / Oathkeeper не разворачиваем** на Track B (как и на Track A) — permissions через свои таблицы в БД, reverse-proxy не нужен | ArchGate, 22 мая |
| Р-22-6 | **Google-аккаунт = OIDC federation поверх IdP** (не вместо). IdP (Ory Kratos) остаётся обязательным — управляет локальными identity, выдаёт JWT, держит сессии, делает audit | Переписка с Андреем, 22 мая |
| Р-22-8 | **Login-методы Track B (мир):** Email + Magic Link, Sign in with Google, Sign in with Apple (если будет iOS-приложение — обязательно по App Store policy), Sign in with GitHub (опционально под developer-аудиторию), Passkey/WebAuthn (на будущее) | Переписка с Андреем + ArchGate, 22 мая |
| Р-22-9 | **Login-методы Track A (Россия):** Email + Magic Link, Yandex ID, Telegram Login Widget, VK ID (опционально) — Ory всё поддерживает через OIDC-providers | ArchGate, 22 мая |

## Е. AI-архитектура и multi-channel

| ID | Решение | Источник |
|---|---|---|
| Р-22-3 | **AI-ядро (orchestrator) выносим из бота на платформу** — WP-262 активация Q2-Q3. Telegram = один из адаптеров; RU/world = параметр `locale` в одном orchestrator'е, а не отдельные orchestrator'ы. Каналы: Telegram (RU/мир), Web chat widget, WhatsApp Business, Slack, claude.ai/ChatGPT через MCP, VS Code/Cursor через MCP — все как тонкие клиенты | Переписка с Андреем + WP-262, 22 мая |

## Ж. Миграции БД

| ID | Решение | Источник |
|---|---|---|
| Р-22-4 | **Миграции = app-startup self-migrate** через Alembic + `pg_advisory_lock` (multi-replica safe). **Werf-хук не используется** — это уровень приложения, не инфраструктуры. Исключение: тяжёлые миграции (rewrite больших таблиц, индексы на миллионах строк) — отдельный admin-процесс в maintenance window | Переписка с Андреем, 22 мая |

## З. Безопасность и наблюдаемость

| ID | Решение | Источник |
|---|---|---|
| Р-инв-9 | **Fernet pgcrypto setup до первого insert** в `payment_registry` (DP.ARCH.004 §1 v2.3) | Inventory §3 |
| Р-инв-10 | **Fernet keys в K8s Secret** до первого OAuth-flow для БД `secrets` (ADR-004, 14 мая) | Inventory §3 |
| Р-инв-11 | **Better Stack мониторы для Track B** с обязательным keyword-check (HD #51 — HTTP 200 + 0 bytes = false-green) | Inventory §4 |
| Р-инв-12 | **Secret Drift Detector** pipeline для Track B секретов до Фазы 5 (WP-315) | Inventory §4 |

---

## Открытые вопросы

> **Статус на 9 июня 2026:** встречи 21–23 прошли (май 2026), часть вопросов ниже могла быть закрыта. Требуется проверка по итогам transcript'ов встреч 21–23 и встречи 24 (4 июня).
>
> *(Исходная формулировка ниже — выносилось на встречу 24 мая)*

> Не решения — кандидаты на решение. После встречи мигрируют наверх с новым ID `Р-24-N`.

| Тема | Контекст |
|---|---|
| **CF Workers — детализация Р-22-1** | Переносить ли `event-gateway` и `payment-receiver` в GKE? Кто пишет, сколько часов? |
| **WP-262 orchestrator host** | Где живёт: CF Worker / Railway / новый сервис на GKE / расширение Aisystant MCP? Активация — какой месяц Q2-Q3? Связь с Track B MVP |
| **Track B бот стартует как «тонкий клиент» или повторяет Track A?** | Strangler vs greenfield для нового бота |
| **Multichannel в Track B MVP** | Только Telegram? + Web chat widget на aisystant.com сразу? |
| **Domain naming для Track B** | Схема имён для 10 CF Workers + Ory + бот. `mcp.aisystant.com` → переезжает на Track B и Track A получает `mcp.aisystant.ru`? Покупка `aisystant.ru` — статус? |
| **Миграции — детализация Р-22-4** | Alembic для всех Python-сервисов? Структура хранения миграций — стандарт? «Тяжёлая миграция» — формальная граница? |
| **payment-registry deployment** | Нет Dockerfile (WP-307 Ф1). Создаём или другой паттерн? |
| **google-drive-mcp** | Python в GKE или портировать в TypeScript CF Worker (связано с Р-22-1)? |
| **Metabase для Track B** | Поднимаем сразу или отложить до накопления данных (сейчас в inventory §7)? |
| **WP-228 Ф32** | `subscription.contract_event` пустая 6 недель при 541 active subs — projection-worker не пишет? Диагностика обязательна до Track B, иначе наследуем gap |
| **Railway deploy method** | 5 сервисов peaceful-vision деплоятся через `railway up` (manual). Пересоздать через GitHub Actions → Artifact Registry до миграции в GKE (WP-307 Ф5b) |
| **Stripe — юрисдикция (Р-22-7)** | ИП Тсерена / ООО / Foundation. Влияет на бухгалтерию + tax-reporting |
| **TG-боты и observability** | Имя бота для Track B (`@aisystant_world_bot`?); кто регистрирует. Отдельный TG-чат для алертов Track B |
| **Бэкапы Cloud SQL** | Аналог DP.SC.131 для Cloud SQL — кто пишет (PITR + daily в GCS)? Backup-стресс-тест перед запуском первого пользователя — gate? |
| **Календарь команды** | Паша вышел 18 мая — что готово, какие первые задачи? Когда Андрей переключает основной фокус с Track A? Ильшат — % handover'а? |

---

## История изменений реестра

| Дата | Что изменилось | Источник |
|---|---|---|
| 2026-05-22 | Создан реестр. Консолидированы решения Р-14-* (встреча 14), Р-15-* (оперативка 14 мая), Р-инв-* (inventory + DP.SC.131), Р-22-* (переписка с Андреем + ArchGate Ory vs Zitadel) | Сессия 22 мая |
