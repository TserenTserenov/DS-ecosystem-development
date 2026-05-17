---
type: inventory
title: "Список сервисов: Track A → Track B"
status: draft
created: 2026-05-07
updated: 2026-05-17
author: Церен
---

# Список сервисов: что есть и что нужно на мировой платформе

> **Track A (Россия)** — работает как есть, ничего не трогаем.
> **Track B (Мир)** — новый независимый деплой. Каждый сервис получает свою копию.
> «Дублировать» = развернуть новый инстанс с тем же кодом, но указывающий на Track B инфраструктуру (Cloud SQL, Ory EU, Stripe).
>
> **Scope этого документа** — MVP-сервисы для онбординга первого пользователя Track B (16 сервисов: 11 CF Workers + 5 Python). Полный operational scope production-runtime — **31 deployment unit**, см. [`C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-services.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-services.md) (WP-307). Сервисы вне MVP-scope — раздел §7.

---

<details>
<summary><b>1. CF Workers (Cloudflare) — 10 сервисов</b></summary>

Все работают на Cloudflare Workers (TypeScript). Код тот же, меняются только переменные окружения (DATABASE_URL, ORY_URL, STRIPE_KEY и т.д.).

| Сервис | Что делает | Внешний endpoint | Домен Track B | Dockerfile | Track A | Track B | Примечания |
|--------|-----------|-----------------|--------------|------------|---------|---------|------------|
| **gateway-mcp** | API-шлюз: OAuth, роутинг по доменам, MCP-точка входа | **да** (HTTPS MCP + OAuth) | TBD (напр. `mcp.world.aisystant.com`) | нет (CF Worker) | `mcp.aisystant.com` | новый домен | Обновить Hyperdrive binding → Cloud SQL |
| **knowledge-mcp** | Поиск по базе знаний (Pack, guides, SOTA, граф концептов) | **да** (HTTPS MCP) | TBD | нет (CF Worker) | Neon #7 knowledge | Cloud SQL knowledge | Переиндексировать граф под EN-контент |
| **personal-knowledge-mcp** | Личная база знаний пользователя (заметки, эмбеддинги) | **да** (HTTPS MCP) | TBD | нет (CF Worker) | Neon #1 persona | Cloud SQL persona | Обновить строку подключения |
| **digital-twin-mcp** | Показатели, состояния, прогресс ученика | **да** (HTTPS MCP) | TBD | нет (CF Worker) | Neon #5 indicators | Cloud SQL indicators | Обновить строку подключения |
| **guides-mcp** | Каталог программ и руководств | **да** (HTTPS MCP) | TBD | нет (CF Worker) | Neon #8 reference | Cloud SQL reference | Загрузить EN-программы |
| **event-gateway** | Единственный writer событий в journal | **да** (HTTPS POST от сервисов) | TBD | нет (CF Worker) | Neon #2 journal | Cloud SQL journal | Обновить строку подключения |
| **fsm-mcp** | Конечный автомат ассистента ученика | **да** (HTTPS MCP) | TBD | нет (CF Worker) | stateless | stateless | Переменные среды под Track B |
| **payment-receiver** | Webhook от платёжных систем | **да** (Stripe webhook) | TBD | нет (CF Worker) | YooKassa | **Stripe только** | Новый handler для Stripe webhooks |
| **observability-webhook** | Better Stack → TG-алерты об инцидентах | **да** (webhook от Better Stack) | TBD | нет (CF Worker) | stateless | stateless | Новый TG-бот / чат для Track B |
| **status-proxy** | Редирект на страницу статуса платформы | **да** (HTTP redirect) | `status.TBD.com` | нет (CF Worker) | `status.aisystant.com` | новый домен | Обновить CNAME |

> **CF Workers: Dockerfile не нужен** — деплой через `wrangler deploy` или GitHub Action → Cloudflare. Домены нужны для всех 10 воркеров (обсудить с Андреем единую схему именования Track B на встрече 18 мая).
>
> **Уточнение 17 мая:** `google-drive-mcp` ранее считался CF Worker — на самом деле это Python MCP server (нет `wrangler.toml`, есть `mcp_server.py`). Перенесён в §2 Python-сервисы.

**Что нужно сделать общее:** создать новый `wrangler.toml` или `.env` под Track B для каждого воркера. Деплоить в тот же Cloudflare-аккаунт, но с другими именами и привязками.

</details>

<details>
<summary><b>2. Python-сервисы (контейнеры) — 6 сервисов</b></summary>

Сейчас живут на Railway (5 сервисов) + один локальный Python MCP (`google-drive-mcp`). Для Track B: GKE Standard (K8s Deployment или CronJob).

| Сервис | Что делает | Внешний endpoint | Домен Track B | Dockerfile | Track A deploy | Track B | Тип |
|--------|-----------|-----------------|--------------|------------|---------------|---------|-----|
| **aist_bot_newarchitecture** | Telegram-бот (@aist_me_bot, @aist_pilot_me) | **нет** (Telegram pull) | не нужен | ✓ | Railway, `railway up` manual ⚠️ | GKE Deployment | Deployment |
| **multi-domain-projection-worker** | Проекции событий → persona / subscription / indicators | **нет** (читает БД) | не нужен | ✓ | Railway, **не задеплоен** (ждёт WP-270) 🟡 | GKE CronJob | CronJob |
| **rewards-projection-worker** | Расчёт баллов и достижений | **нет** (читает БД) | не нужен | ✓ | Railway, `railway up` manual ⚠️ | GKE CronJob | CronJob |
| **activity-hub** | Сборщик событий (medallion: bronze/silver/gold) | **нет** (читает journal из БД) | не нужен | ✓ | Railway, `railway up` manual ⚠️ | GKE Deployment | Deployment |
| **payment-registry** | Единый журнал транзакций | **нет** (внутренний API) | cluster-internal | **⚠️ TBD** — нет Dockerfile в корне (WP-307 Ф1) | TBD | GKE Deployment | Deployment |
| **google-drive-mcp** | Интеграция с Google Drive (Python MCP server) | **да** (HTTPS MCP + OAuth callback) | TBD | TBD (сейчас `python mcp_server.py` без build) | локально/stateless | GKE Deployment | Deployment |

> **Python-сервисы: Dockerfile ✓ у 4 из 6** — подтверждено Андреем 14 мая. **Открытые:** payment-registry (нет Dockerfile, WP-307 Ф1) + google-drive-mcp (новый — нужен Dockerfile под GKE). Решить до Фазы 3.3.
>
> **⚠️ Deploy method gap (WP-307 Ф5b):** Все Railway-сервисы peaceful-vision деплоятся через `railway up` (manual upload), без git→deploy linkage и без immutable release artifact. Это нарушение F1/F5 12-factor. Перед миграцией в GKE — пересоздать deploy через GitHub Actions → Artifact Registry → Werf (см. track-b-plan §1.11).

**Не переносить на Track B:**
- **bridge-2-events-poller** — polling legacy LMS Aisystant. Legacy LMS только российская, для Track B не нужен.

**Прерывистый риск миграции (WP-228 Ф32, 14 мая):**
- `subscription.contract_event` в Track A пуста 6 недель при 541 active subscriptions — projection-worker для subscription, скорее всего, не пишет. До миграции в Track B — диагностика W3/W4 (cursor advance vs schema mismatch). Иначе Track B унаследует gap. См. lessons_dual_run_event_catalog_gaps.

**Что нужно сделать общее:** Werf-манифест + K8s manifest (env vars из Secret, указывающие на Cloud SQL, Ory EU). Dockerfile у 4 из 6 уже есть.

</details>

<details>
<summary><b>3. Базы данных — 12 Neon → 12 Cloud SQL</b></summary>

Track A: остаются в Neon как есть. Track B: новые инстансы в Cloud SQL (europe-west4, тот же регион что кластер).

| # | БД | Что хранит | Track B — что сделать |
|---|----|-----------|----------------------|
| 1 | **persona** | Аккаунты, настройки, личные заметки, эмбеддинги | Создать схему, пустая |
| 2 | **journal** | Все события платформы (event sourcing) | Создать схему, пустая |
| 3 | **payment** | Платежи, возвраты, методы оплаты | Создать схему + **добавить Stripe-поля** |
| 4 | **subscription** | Подписки, автопродления, аудит | Создать схему, пустая |
| 5 | **indicators** | Показатели, baseline, снапшоты прогресса | Создать схему, пустая |
| 6 | **learning** | Курсы, прогресс, задания, менторинг | Создать схему + загрузить EN-контент |
| 7 | **knowledge** | Граф концептов, индексы, эмбеддинги | Создать схему + переиндексировать |
| 8 | **reference** | Тарифы, программы, справочники | Создать схему + **загрузить мировые тарифы** |
| 9 | **publication** | Статьи, посты, каналы публикаций | Создать схему, пустая |
| 10 | **community** | Наставничество, встречи, группы | Создать схему, пустая |
| 11 | **lead** | Лиды, UTM-визиты, воронка | Создать схему, пустая |
| 12 | **rewards** | Баллы, достижения, квалификации | Создать схему + **новая эмиссия для Track B** |

**Итог:** Схемы берутся из Neon (pg_dump --schema-only). Данные НЕ мигрируются — Track B стартует пустым. Пользователи Track A могут перейти через экспорт/импорт (WP-285 Ф6).

</details>

<details>
<summary><b>4. Внешние сервисы</b></summary>

| Сервис | Track A | Track B | Что делать |
|--------|---------|---------|-----------|
| **Ory (auth)** | VK Cloud (RU) | GKE EU, отдельный инстанс | Развернуть Ory Kratos + Hydra на GKE, своя БД |
| **Cloudflare** | DNS + Workers + DDoS | Тот же аккаунт | Новые DNS-записи для Track B домена |
| **YooKassa** | Платежи (рубли) | — | **Не нужен на Track B** |
| **Stripe** | — | Платежи (USD/EUR/...) | Зарегистрировать аккаунт, получить ключи |
| **Better Stack** | Мониторинг Track A (10 мониторов) | Новые мониторы для Track B | **Обязательно keyword-check** для каждого endpoint (HTTP 200 + 0 bytes = false-green, HD #51) |
| **Telegram** | Бот @aist_me_bot | Новый бот для Track B | Зарегистрировать нового бота через @BotFather |
| **GitHub** | org: `aisystant` | Новая отдельная организация | Паша создаёт, форкает нужные репо |
| **Terraform Cloud** | — (Track A без него) | IaC для GKE, Cloud SQL, сети | Паша настраивает отдельный репо |
| **Google Cloud** | — | GKE Standard + Cloud SQL + Artifact Registry (europe-west4) | Церен регистрирует аккаунт, $300 кредит |
| **Metabase** (Аттестатор) | Self-hosted, читает `learning` и `indicators` (Аттестатор RCS) | Решение — нужен ли отдельный инстанс для Track B | Сейчас Track A only; для Track B решить после онбординга первых пользователей (когда наберётся достаточно событий для аналитики). До тех пор — N/A |
| **Secret Drift Detector** (WP-315) | Sentinel сравнения секретов между Layer 1 (Neon/Cloudflare/Railway) и Layer 2 (1Password/GitHub Secrets) | Аналогичный pipeline для Track B | До Фазы 5 — настроить detector на Track B секреты, иначе drift не виден |

</details>

<details open>
<summary><b>5. Итог: приоритет для старта 18 мая</b></summary>

Минимальный набор, чтобы хотя бы один пользователь смог зарегистрироваться и начать работу:

1. **GKE кластер + Cloud SQL + Artifact Registry** — Паша (18-19 мая, track-b-plan §1.1-1.6)
2. **Ory EU (Kratos + Hydra на GKE)** — авторизация без него ничего не работает (25-31 мая, Фаза 2)
3. **gateway-mcp** — точка входа в платформу
4. **event-gateway** — без него события не пишутся
5. **aist_bot_newarchitecture** — основной интерфейс пользователя
6. **БД: persona, journal, subscription** — три ключевые для онбординга

Остальные можно поднимать итеративно после первого пользователя.

**Prerequisites закрытия до старта Фазы 1 (17 мая):**
- ✅ Инвентарь актуален (этот документ, 17 мая)
- ✅ 12-factor compliance аудит (WP-307 закрыт 13 мая, см. [`12factor-services.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-services.md))
- 🔄 GCP-аккаунт + $300 кредит (Тсерен, 17 мая)
- 🔄 Документ разграничения (§6 этого файла; Андрей детализирует к 17 мая)
- 🔄 Согласование схемы доменов Track B на встрече 18 мая
- ⚠️ Диагностика projection-worker для `subscription.contract_event` (до миграции, WP-228 Ф32)

</details>

<details>
<summary><b>6. Разграничение ответственности: Разработчик (Андрей) vs DevOps (Паша)</b></summary>

> Документ подготовлен к встрече 18 мая (Пашин выход). **Андрей оформит детально** до 17 мая.
> Принцип: разработчик пишет код + Dockerfile, DevOps разворачивает инфру и принимает артефакты.

| Зона | Разработчик (Андрей) | DevOps (Паша) |
|------|---------------------|--------------|
| **Код и Dockerfile** | Пишет, поддерживает Dockerfile для всех Python-сервисов | — |
| **CF Workers деплой** | wrangler.toml / GitHub Action → Cloudflare | — |
| **Werf-манифест** | Пишет минимальный манифест (env, image, replicas) | Принимает, добавляет инфра-специфику |
| **GKE кластер** | — | Создаёт через Terraform, управляет нодами |
| **Cloud SQL** | Пишет миграции (SQL файлы) | Создаёт инстанс, выдаёт строку подключения |
| **Secrets (K8s)** | Указывает список нужных env vars | Создаёт K8s Secret, заполняет значения |
| **Ory EU** | Указывает нужные scopes/flows | Разворачивает Kratos+Hydra, выдаёт эндпоинты |
| **Домены + DNS** | Указывает какой сервис нуждается в домене | Настраивает DNS, SSL, Cloudflare rules |
| **Мониторинг** | Пишет что алертить (endpoint, keyword) | Создаёт Better Stack мониторы |
| **CI/CD pipeline** | Пишет GitHub Action для сборки образа | Настраивает деплой из реестра → GKE |

**Принцип «разработчик не знает паролей»:** разработчик передаёт образ + манифест → DevOps заполняет секреты и деплоит. Разработчик не имеет прямого доступа к prod БД.

**Открытые вопросы (обсудить 18 мая):**
- [ ] Схема именования доменов Track B (10 CF Workers + google-drive-mcp Python + Ory + бот нуждаются в доменах)
- [x] ~~Где хранится container registry~~ → решено: **GCP Artifact Registry** (track-b-plan §1.6)
- [x] ~~Как разработчик триггерит деплой в GKE~~ → решено: **PR merge → GitHub Action → Artifact Registry → Werf → GKE** (track-b-plan §1.11)
- [x] ~~Ory EU: GKE или Vultr VPS~~ → решено: **GKE EU** (track-b-plan §2.2-2.3, ADR-IWE-015/016 revision до 30 мая)
- [ ] **Новый:** payment-registry — какой deployment model (нет Dockerfile)? Создать Dockerfile или использовать другой паттерн?
- [ ] **Новый:** google-drive-mcp Python MCP — портировать в TypeScript CF Worker или оставить Python в GKE?
- [ ] **Новый:** Metabase для Track B — поднимать сразу или отложить до набора аналитических данных?

</details>

<details>
<summary><b>7. Сервисы вне scope Track B (operational only)</b></summary>

> Эти сервисы — часть полного production-runtime (31 deployment unit per WP-307), но в Track B **не мигрируются**. Они остаются на инфраструктуре пилота / Track A.

| Категория | Сервисы | Где живут | Почему не в Track B |
|-----------|---------|-----------|---------------------|
| **Autonomous agents** | A1 auditor, A2 idea-scout, A3 orchestrator, A4 tailor, A5 tester, A6 verifier | VPS tsekh-1 (systemd timers, GHCR images) | Личные агенты пилота, не пользовательская инфра |
| **Profiler** | P1 DT Profile Calculator (S52) | macOS launchd (ноутбук пилота) | Per-user расчёт, не shared service |
| **Local scheduler** | T1 per-role launchd plists | macOS launchd (ноутбук пилота) | Личный scheduler пилота |
| **Local Gateway** | L1 iwe-local-gateway (DP.IWE.005) | Unix socket, single-user (ноутбук пользователя) | По дизайну — локально у каждого пользователя, не shared infra |
| **Server tooling** | X2 hetzner-backstage, X3 ssm2025 | Hetzner VPS + Nomad | Backstage-инфра для ops, не пользовательский слой |
| **Admin processes** | AD1 neon-migrations | Manual `psql` | Admin (Factor 12), не runtime; для Track B аналог — migrations через Werf hook |
| **Bridge (legacy)** | bridge-2-events-poller | Railway | Polling legacy LMS Aisystant (Track A only) |

**Полный реестр и деталиrationale:** [`C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-services.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-services.md) §«Принципы включения / исключения».

</details>

<details>
<summary><b>8. Связанные документы</b></summary>

| Документ | Назначение |
|----------|-----------|
| [`WP-285-track-b-plan.md`](WP-285-track-b-plan.md) | Детальный план реализации Track B (фазы 0-6, дедлайн MVP — конец июня) |
| [`12factor-services.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-services.md) | Полный реестр production-runtime (31 deployment unit) + deploy-method matrix |
| [`12factor-matrix.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-matrix.md) | Compliance-матрица по 12 факторам для каждого сервиса (WP-307) |
| [`12factor-report-wp307.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/12factor-report-wp307.md) | Итоговый отчёт аудита 12-factor (закрыт 13 мая) |
| [`security-posture.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/security-posture.md) | Security posture dashboard (B7.x compliance) |
| [`platform-ops-dashboard.md`](../../C.IT-Platform/C2.IT-Platform/C2.3.Operations/platform-ops-dashboard.md) | Единая точка входа в наблюдаемость (WP-302 Ф4) |
| [`B2.1-secrets-inventory.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Identity-and-Access/B2.1-secrets-inventory.md) | Реестр секретов + ротация (релевант для Track B prerequisites) |
| [`DP.D.030-deployment-topology.md`](../../C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Stack-and-Infrastructure/DP.D.030-deployment-topology.md) | Архитектурная топология деплоя |

</details>

<details>
<summary><b>9. Обновления 14-17 мая (changelog)</b></summary>

| Дата | Что изменилось | Источник |
|------|----------------|----------|
| 14 мая | Базовая актуализация: колонки endpoint/домен/Dockerfile добавлены, подтверждены Андреем на оперативке 14 мая | оперативка ИТ 15 |
| 15 мая | Backup-процессы для Track B стандартизированы — DP.SC.131 (backup-stress-test PASS) | WP-317 |
| 16 мая | **Metabase Аттестатор** добавлен в operational dashboard (новый сервис для Track A; для Track B — решить в §7) | WP-310 Ф8 |
| 17 мая | **M6 google-drive-mcp уточнён:** Python MCP server, не CF Worker (factor 7 port-binding отличается). Перенесён в раздел Python-сервисов | WP-307 Ф1 |
| 17 мая | **Deploy-method gap для Railway:** B1/B2/W1/W2/W4 деплоятся через manual `railway up` (нет git→deploy linkage). Закрытие F1/F5 — prerequisite для миграции в GKE | WP-307 Ф5b |
| 17 мая | **W5 payment-registry — TBD deployment model:** нет Dockerfile в корне, нужно уточнить до Фазы 3.3.5 | WP-307 Ф1 |
| 17 мая | **WP-228 Ф32 алерт:** `subscription.contract_event` пустая 6 недель при 541 active subscriptions — диагностика projection-worker до миграции в Track B | lessons_dual_run_event_catalog_gaps |
| 17 мая | Добавлен §7 «Сервисы вне scope Track B» — autonomous agents (A1-A6), profiler (P1), launchd (T1), hetzner-backstage (X2), ssm2025 (X3) — остаются в инфре пилота/Track A | WP-307 Ф0 |

</details>
