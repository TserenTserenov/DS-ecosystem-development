---
title: "Security Posture Dashboard"
type: security-dashboard
wp: WP-212
status: active
created: 2026-05-08
updated: 2026-07-15 (автономный прогон WP-212: +§6.3 FDW dependency map)
next_audit: 2026-08-04 (Month Close август; требует починки авто-аудитора — см. WP-458 ВЫ-7)
last_full_audit: 2026-07-02 (WP-458 сквозной аудит, 6 доменов)
owner: WP-212
audit_cadence:
  daily: tsekh-1 systemd-timer 04:45 МСК — VR.R.002 daily-headless по B7.4 A-D (~10-15 мин, $1.5)
  weekly: Week Close — quick check (2 мин, open_critical_count > 0?)
  monthly: Month Close — VR.R.002 monthly-deep по B7.4 A-F (~1h, $5, обновить все секции)
  per_arch: ArchGate §Б — при добавлении нового сервиса (STRIDE + чеклист)
related:
  protocol: DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Identity-and-Access/B7.4-external-audit-checklist.md
  threat_model: DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Identity-and-Access/B7.2-stride-threat-model.md
  pii_map: DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Data-Governance/B3.1-pii-field-map.md
---

# Security Posture Dashboard

> **Источник правды:** WP-212 (Программа безопасности продуктов).
> **Обновляется:** автоматически при закрытии задач WP-212, вручную — VR.R.002 Аудитор при Month Close.
> **Назначение:** единая точка для быстрой оценки состояния безопасности, подготовки к внешнему аудиту, принятия решений о приоритетах.

---

## ⚠️ Сверка WP-458 (2026-07-02) — дашборд отставал 7 недель

> **Процессный дефект (устраняется):** авто-аудитор (launchd `com.iwe.overnight-auditor`, 01:30) запускается ежедневно, но с ~13 июня делает «рефлекс-пропуск» (глубокий разбор только при изменении Python-кода) и **не обновляет этот дашборд вообще** (в `scripts/overnight-auditor.sh` нет записи в security-posture/commit). Последний реальный аудит-срез — 14 мая. Выхлоп `DS-agent-workspace/auditor/` остановился 13 июня. Починка петли «аудитор → дашборд» — задача WP-458 ВЫ-7.

**Исправления ложных утверждений §4:** заявленное «8/8 Dependabot» — неверно (0 конфигов `dependabot.yml` во всех репо). §4-таблица не включала секрет-чувствительные `payment-registry`, `neon-migrations`, `iwe-local-gateway` (у них 0 сканеров и незащищённый `main`).

**Новые критические из WP-458** (сверх известных B2.5/B4.23/B3.6/B3.9 — они подтверждены):
1. Подделка платёжного вебхука → бесплатный доступ (нет подписи + нет серверной сверки с YooKassa) — бот `/webhook/yookassa,/webhook/workshop-payment` + `payment-receiver`.
2. Шлюз событий `event-gateway /events` без аутентификации производителя → выдача наград/подписок.
3. Prompt injection → выполнение произвольного кода в headless-агенте (`iwe-agent-dispatcher.py`) + cron вливает живые секреты без секрет-хуков.
4. Email пользователей в прод-логах бота (`google_calendar_oauth.py:207`, `oauth_server.py:688`) — блокер.
5. Grafana API-ключ литералом в `~/IWE/.mcp.json` (наружу не ушёл — нет remote; ротировать).
6. Платёжный код на личном GitHub-аккаунте + GHAS secret scanning off + коммиты не подписаны (вектор WP-401).

**Полный реестр:** `DS-my-strategy/inbox/WP-458/f1-findings.md` (все 6 доменов) + `f2-triage.md` (ранжирование + план волн).
**Устранено на 2026-07-02:** секрет-паттерны в `~/IWE/.gitignore` (ВЫ-4, Волна 0).

---

## 1. Общий уровень зрелости (Security Maturity Score)

> **Методика:** 5 измерений × 4 уровня (0-3). Уровень 1 = базовая гигиена. Уровень 2 = повторяемые процессы. Уровень 3 = измеряемое + автоматизированное. Conjunctive: итоговый = **min по измерениям** (самое слабое место определяет общий уровень).

| Измерение | Уровень | Обоснование | Целевой Q3 |
|-----------|---------|-------------|------------|
| **Governance** (политики, роли, ответственность) | 1.5 | Политики есть (B2.3 ротация, B3.5 retention, B3.8 privacy draft). Формального security owner нет, DPA с провайдерами отсутствует | 2 |
| **Design** (threat modeling, secure design) | 2 | STRIDE B7.2 (draft, 8 сервисов). ArchGate §Б встроен в каждый РП. Data classification map B7.3.1 готова | 2.5 |
| **Implementation** (secure coding, CI/CD) | 2 | SAST (bandit/semgrep), TruffleHog, Dependabot, branch protection. RLS на knowledge-mcp ✅, JWT-верификация в 3 MCP ✅. OAuth tokens шифрование (B2.5) — pending | 2.5 |
| **Verification** (security testing) | 1 | E2E изоляция 5/5 PASS (B4.15). Нет формального pentest. Нет автоматизированных security regression tests | 2 |
| **Operations** (мониторинг, incident response) | 1.5 | Alerter (WP-244) работает. DR runbook есть (B6.3). Audit trail частичный (WP-237 pending). GDPR erasure нет | 2 |

**Итоговый уровень (min):** **1** (Verification — самое слабое)
**Целевой Q3:** **2** (все измерения ≥ 2)

---

## 2. Прогресс WP-212 по фазам

| Фаза | Задач | Сделано | % | Ближайший незаблокированный шаг |
|------|-------|---------|---|----------------------------------|
| Ф1 Критические | 8 | 8 | 100% | ✅ — |
| Ф2 Секреты | 5 | 5 | 100% | ✅ WP-315 Ф-Close (automator tsekh-1 04:45 МСК + VR.R.002 daily-headless) |
| Ф3 Данные пользователей | 9 | 5 | 56% | B3.6 GDPR erasure, B3.9 consent (dep: aist_bot) |
| Ф4 Auth Hardening | 17 | 15 | 88% | B4.23 пр.1 (dep WP-231), B4.23 пр.2 (dep WP-227) |
| Ф5 CI/CD | 6 | 5 | 83% | B5.6 private repos (dep GitHub Pro) |
| Ф6 Backup/DR | 4 | 4 | 100% | ✅ — |
| Ф7 ArchGate | 14 | 11 | 79% | B7.3.6 доступ Павла (требует пользователя) |
| Ф8 Compliance | 8 | 1 | 13% | B3.8 Privacy draft ✅; B8.0 ToS+Privacy v0.1 draft ready, не опубликован; B8.1-B8.5 dep WP-186 |
| Ф9 Neon RLS roll-out | 7 | 1 | 14% | B9.x dep WP-228 |
| **Итого** | **78** | **54** | **69%** | — |

---

## 3. Открытые уязвимости (по критичности)

> Обновляется VR.R.002 Аудитором при каждом аудите. Источник: STRIDE B7.2 + ArchGate §Б + incident log.

| Критичность | Кол-во | Примеры | Дедлайн |
|-------------|--------|---------|---------|
| 🔴 критическая | 2 | B2.5 OAuth tokens plaintext в БД; B4.23 пр.2 RLS на digital_twins/users | dep WP-234/WP-227 |
| 🟡 высокая | 4 | B4.9 Auth events log нет; B7.2 draft (не review); B8.0 ToS/Privacy нет; Variant E (JWT claim) pending Паша | W19-W20 |
| 🟢 средняя | 6 | B3.6 GDPR erasure; B3.7 activity hub bulk sync; B3.9 consent UI; B4.1 API RBAC; B7.4 external audit prep; B9.x RLS roll-out | W20-W21 |
| ⚪ низкая | 4 | B5.5 container scan; FSM concurrency lock; GitHub App scope re-consent; timing side-channel | backlog |
| **Итого** | **16** | — | — |

### 3.1 Feature-flag security gates (pre-mitigations)

> Флаги, удерживающие потенциальный вектор закрытым до выполнения условия снятия. Снимает пилот **вручную** после закрытия условия (не автодеплоем). Источник: WP-417 ArchGate 2026-06-13 (инвариант И3), запись 2026-06-14.

| Флаг | Где | Что гейтит | Условие снятия | Статус |
|------|-----|-----------|----------------|--------|
| `FEATURE_F5_PLATFORM_RENDER` | `DS-my-strategy/scripts/lib/panel_render.py` | Рендер тайлов баллы/бонусы/ступень/время (WP-417 Ф5) на публично-смежной guide-web — вектор утечки PII | **L1 local:** B7.3 пройден (2026-06-16); флаг `True`. **L3 guide-web:** B7.3 §Б пройден (2026-06-16): класс=PII-смежное (поведенческие метрики пилота), логирование exception-only ✅, Neon at-rest ✅, RLS debt в source-таблицах (РП121/РП318), SQL параметрирован ✅, TLS+HTTPS ✅. 0 ❌, 2 ⚠️ (RLS source, B2.1 inventory). Код в DS-my-strategy (bdf46ea1a) импортируется tsekh-1 автоматически через относительный путь. **Prod Neon storage** (`learning.user_panel_daily` + `learning.user_panel_audit`): B7.3 §Б пройден (2026-06-17): класс=PII-смежное (account_id + поведенческие метрики), логирование exception-only ✅, Neon at-rest ✅, RLS debt (tech-debt), SQL параметрирован ✅, TLS ✅, один writer (воркер) + read-only checker ✅. 0 ❌, 2 ⚠️ (RLS, PII-смежное). tsekh-1: `NEON_LEARNING_URL`/`NEON_REWARDS_URL` добавлены в `panel.env` + `PYTHONPATH` в service file (2026-06-17). Smoke PASS: чекер `целостна (7 дней)`. | ✅ `True` (L1 + L3 prod Neon активны) |

---

## 4. CI/CD Security Coverage

> **Источник (WP-458 ВЫ-7):** таблица генерируется детерминированно скриптом `DS-my-strategy/scripts/security-coverage-sync.sh` (живой опрос через `gh api`, без LLM). Не редактировать между маркерами вручную.

<!-- COVERAGE-SYNC:START (generated by security-coverage-sync.sh, 2026-07-23T18:34Z) -->

| Репо | Secret scanning | Scan workflow | SAST | Branch protection (default) | Dependabot |
|------|-----------------|---------------|------|-----------------------------|------------|
| aisystant/aist_bot | enabled | нет | да | нет | нет |
| aisystant/activity-hub | нет | да | да | нет | нет |
| aisystant/event-gateway | нет | нет | да | нет | нет |
| aisystant/gateway-mcp | нет | да | да | нет | нет |
| aisystant/payment-receiver | нет | нет | да | нет | нет |
| aisystant/digital-twin-mcp | enabled | да | да | да | нет |
| aisystant/personal-knowledge-mcp | нет | да | да | нет | нет |
| aisystant/knowledge-mcp | enabled | да | да | да | нет |
| aisystant/github-integration-service | нет | нет | нет | нет | нет |
| aisystant/multi-domain-projection-worker | нет | нет | нет | нет | нет |
| aisystant/rewards-projection-worker | нет | нет | нет | нет | нет |
| TserenTserenov/payment-registry ⚠️личный | нет | нет | нет | нет | нет |
| TserenTserenov/neon-migrations ⚠️личный | нет | нет | нет | нет | нет |
| iwesys/iwe-local-gateway | нет | нет | нет | нет | нет |

> Сгенерировано детерминированно (gh api, без LLM) 2026-07-23T18:34Z. Не редактировать вручную между маркерами.
<!-- COVERAGE-SYNC:END -->

**Реальное покрытие (2026-07-02):** Secret scanning 3/14 · Scan workflow 5/14 · SAST 5/14 · Branch protection 2/14 · **Dependabot 0/14**.

**Красные зоны:** `payment-registry` (личный аккаунт, платежи) и `event-gateway`/`payment-receiver` (эксплуатируемые критические эндпоинты) — по нулям во всех колонках. Dependabot не настроен нигде (прежнее «8/8» было ложным).

### 4.1 Infrastructure Secret Scanning (Runtime)

> **Automator:** tsekh-1 (systemd timer daily at 04:45 МСК)
> **Artifact:** WP-315 Ф-Close (Secret Drift Detector) — see DP.SC.125

**Automation Flow:**
1. **Layer 1 (Local):** `iwe-grep-secret.sh` scans `.git/.env` files on tsekh-1
2. **Layer 2 (Railway):** GraphQL API v2 introspection → service vars audit
3. **Layer 3 (Cloudflare):** Workers environment variables scanning
4. **Layer 4 (Neon):** Direct role/password audit (unpooled endpoint)

**Result Flow:** scan results → systemd journal (tsekh-1) → JSON parsing → VR.R.002 daily-headless audit agent (Sonnet) → notification + inventory update

**Detection Scope:**
- Leaked secrets (grep via 50+ patterns: AWS keys, RSA privates, Neon tokens, etc.)
- Misplaced credentials (Layer N secrets should be in Layer M)
- Rotation status (age-check: >90 days flagged)
- Orphaned tokens (auth'n success but source unknown)

**SLA:** Detection latency ≤24h. Notification on **critical** finding within 30 min same day.

---

## 5. Compliance статус

| Требование | Статус | Артефакт | Следующий шаг |
|------------|--------|---------|---------------|
| 152-ФЗ | 🟡 частично | B7.3.5 (L1+L2 достаточно) | Юрконсультация (dep WP-186) |
| GDPR baseline | 🟡 частично | B3.8 Privacy draft | B8.0 публикация + erasure workflow |
| ToS пользователей | 🔴 нет | черновик не опубликован | **B8.0 (~2h, unblocked)** |
| DPA с Neon/Railway/CF | 🔴 нет | — | dep WP-186 |
| YooKassa (PCI DSS) | ✅ карты у YooKassa | B3.2 data flow map | Подтвердить scope ежегодно |

---

## 6. Secret Inventory

> **Источник правды:** WP-315 (Реестр и валидатор инсталляций секретов IWE).
> **Обновляется:** при ротации credential (AR.205 probe), при Month Close (VR.R.002), при добавлении нового сервиса.
> **Назначение:** единая точка для ответа на вопрос «где всё живёт этот секрет?»

### Bootstrap inventory (минимум 3 секрета)

| Секрет | Layer 1 (env) | Layer 2 (cloud) | Layer 3 (PG metadata) | Layer 4 (smoke) | Последняя ротация | Владелец |
|--------|---------------|-----------------|----------------------|-----------------|-------------------|----------|
| **Neon main** `neondb_owner` | `~/.secrets/neon`, tsekh-1 `/etc/iwe/env`, `~/IWE/**/.env` | Railway variables (7 сервисов) | `pg_user_mapping` (rewards, learning, analytics, platform), `pg_subscription` | `SELECT 1` через каждую роль | 2026-05-12 | WP-212 |
| **GitHub App Private Key** `aisystant-knowledge` | `~/.secrets/github`, CF secret (`gateway-mcp`, `personal-knowledge-mcp`) | — | — | GitHub App JWT → installation token (ADR-IWE-004) | 2026-04-15 | WP-212 |
| **Telegram pilot** `aist_pilot_bot` | `~/.secrets/telegram` | Railway variables (aist_bot) | — | Bot webhook test | 2026-03-20 | WP-198 |

### Инструменты (WP-315)

- **Сканер:** `FMT-exocortex-template/scripts/iwe-grep-secret.sh` v0.2.0 (Layer 1 + Layer 2 Railway + Layer 3; CF Workers write-only — скан по значению невозможен by design)
- **Паритет:** `FMT-exocortex-template/scripts/check-setup-update-parity.sh` + `.claude/parity-contract.yaml`
- **FDW rotation:** `DS-IT-systems/neon-migrations/apply-fdw-rotation.sh` + `mvp/215-sync-fdw-credentials.sql`
- **Enforcer:** `PACK-agent-rules/rules/AR.205-rotation-verify-pass.md`
- **Service Clause:** `PACK-digital-platform/08-service-clauses/DP.SC.146-secret-drift-detector.md`

### Чеклист ротации (AR.205 probe)

При изменении секрета X:
1. [ ] Запустить `iwe-grep-secret.sh '<old>'` — записать N hits по слоям
2. [ ] Применить новое значение во всех местах из inventory
3. [ ] Повторить `iwe-grep-secret.sh '<old>'` — assert 0 hits
4. [ ] Повторить `iwe-grep-secret.sh '<new>'` — assert ≥1 hit (confirmation new is deployed)
5. [ ] Smoke-test: каждый сервис из inventory подключается успешно
6. [ ] Обновить колонку «Последняя ротация» в таблице выше

### 6.1 Автоматизация инвентаря (WP-315 Ф4)

> **Automator:** `secret-inventory-sync.sh` (systemd timer, ~05:00 МСК, после VR.R.002)
> **Input:** JSON из systemd journal (Secret Drift Detector results)
> **Output:** обновлённый security-posture.md + git commit

**Механизм:**
1. Secret Drift Detector пишет результаты в systemd journal (Layer 1-4 findings)
2. VR.R.002 daily-headless парсит journal, формирует JSON-сводку
3. `secret-inventory-sync.sh` читает JSON → обновляет §6 таблицу:
   - Обновить колонку «Последняя ротация» (если ротация обнаружена)
   - Добавить новые строки (если обнаружены новые секреты)
   - Отметить orphaned (если найдены в Layer N, но не в inventory)
4. Git commit: `docs(WP-315): secret inventory update YYYY-MM-DD`

**Данные в JSON:**
```json
{
  "timestamp": "2026-05-14T04:45:00Z",
  "findings": [
    {
      "secret_id": "neondb_owner",
      "type": "postgresql_role",
      "layers_found": [1, 2, 3],
      "last_rotated": "2026-05-12",
      "age_days": 2,
      "status": "ok"
    },
    {
      "secret_id": "orphaned_cf_token",
      "type": "cloudflare",
      "layers_found": [3],
      "status": "orphaned",
      "note": "found in CF but not in local inventory"
    }
  ]
}
```

**Вход в скрипт:**
- Путь к JSON-файлу (или journalctl parsing)
- Путь к security-posture.md

**Выход:**
- Изменённый security-posture.md (дифф в §6)
- Git commit + push (optional)
- Лог ошибок в stderr (если дифф не применилась)

**SLA:** Обновление ≤15 мин после Secret Drift Detector. Notification if orphaned secrets found.

### 6.2 Расширение inventory (ручное)

```
Роль: Инженер при ротации (или VR.R.002 при автоматизации)
Шаги:
1. Новый секрет/сервис → добавить строку в таблицу §6
2. Указать все 4 слоя (если слой не применим — "—")
3. Обновить WP-315 context если секрет добавлен в рамках РП
```

### 6.3 FDW dependency map (WP-212 Ф11)

> **Источник:** `DS-IT-systems/neon-migrations/mvp/` (202, 215, 226, 227). Создано 2026-07-15 (автономный прогон WP-212).
> **Зачем:** FDW-credentials живут в `pg_user_mapping.umoptions` (Layer 3) — grep по файлам их не видит (инцидент 14 мая: `multi-domain-projection-worker` копил backlog 63K events из-за старого пароля в FDW-маппинге).

| Локальная БД | Foreign server | Целевая БД | Подключается как | Используется | Риск |
|--------------|----------------|-----------|------------------|--------------|------|
| rewards | learning_srv | learning | **neondb_owner** ⚠️ | `compute_effective_amount()` (streak из domain_event) | owner-роль = макс. blast radius |
| rewards | reference_srv | reference | **neondb_owner** ⚠️ | `compute_effective_amount()` (multipliers, repo_map, reward_rules) | то же |
| rewards | indicators_srv | indicators | **neondb_owner** ⚠️ | `compute_effective_amount()` (calculated_profile.qualification_level, rcs_current.stage) | то же |
| rewards | persona_srv | persona | **neondb_owner** ⚠️ | `compute_effective_amount()` (traits.tier fallback) | то же |
| reference | learning_server | learning | `reference_fdw_reader` ✅ (read-only, SELECT только на club_action_limits) | view `rewards_action_catalog` (WP-325) | least-privilege — эталонный паттерн |

**Ротация FDW-credentials:** `DS-IT-systems/neon-migrations/apply-fdw-rotation.sh` + `mvp/215-sync-fdw-credentials.sql` (атомарный ALTER USER MAPPING по всем серверам БД, audit trail через RAISE NOTICE).

**Открытый долг (Ф11 DoD 2–4, owner: пилот — нужен доступ к Neon):** rewards-серверы (4 шт.) всё ещё на `neondb_owner`. Требуется: создать `fdw_reader_{learning,reference,indicators,persona}` с GRANT SELECT только на нужные таблицы → ALTER USER MAPPING → smoke `compute_effective_amount()`. Паттерн-эталон уже есть: миграции 226/227 (WP-325).

**Чеклист добавления новой FDW-зависимости:**
1. Создать `fdw_reader_<target>` с минимальными правами (НЕ owner-роль).
2. GRANT SELECT только на конкретные таблицы (не PUBLIC, не ALL).
3. Зарегистрировать строку в этой карте (§6.3).
4. Добавить в inventory ротации (§6 таблица + WP-315 сканер).

## 7. История аудитов

| Дата | Тип | Аудитор | Итог | Артефакт |
|------|-----|---------|------|---------|
| 2026-04-08 | Первичный внутренний | Claude (Sonnet) | 13 находок инфры + 10 потоков данных | WP-212 §Сводная таблица рисков |
| 2026-04-12 | Ф1 Remediation | Claude (Sonnet) + Паша | Ф1 ✅, Ф4 80% | WP-212 Ф4 |
| 2026-04-14 | Ф2-Ф7 Deep dive | Claude (Sonnet) | 48/65 DONE, sub-agent верификация PASS | WP-212 Handoff 14 апр |
| 2026-04-28 | STRIDE first-pass | Claude (Sonnet) | 8 сервисов охвачено, 6 open questions | B7.2-stride-threat-model.md |
| 2026-05-08 | Статус ревью | VR.R.002 Аудитор (Sonnet) | 54/78 69%, 14 open vulns, posture level 1; B8.0 ToS+Privacy v0.1 draft ready (публикация pending); VR.R.002 как автономный агент задеплоен | этот файл |
| **с 2026-05-09** | **Daily** | **VR.R.002 daily-headless (tsekh-1)** | автоматически 04:45 МСК | DS-agent-workspace/auditor/YYYY-MM-DD/ |
| **2026-06-01** | Month Close аудит | **VR.R.002 monthly-deep** | ⚠️ не выполнен (авто-аудитор в reflex-skip с ~13 июня) | — |
| **2026-07-02** | Сквозной аудит платформы + IWE | Claude (Fable 5) + 6 параллельных доменных аудиторов | ~50 находок → 8 критических кластеров; 6 доменов; Волна 0 устранена | WP-458 (f1-findings.md, f2-triage.md) |

---

## 8. Ключевые риски (топ-3 на сейчас)

| # | Риск | Вероятность | Impact | Митигация |
|---|------|-------------|--------|-----------|
| 1 | **OAuth tokens в plaintext** — утечка БД aist_bot → все GitHub/Google токены пользователей компрометированы | средняя | критический | B2.5 pending Дима. Interim: Neon AES-256 at-rest + сетевая изоляция |
| 2 | **Нет ToS/Privacy** — YooKassa может заблокировать платежи, GDPR жалоба при первом EU-пользователе | низкая | высокий | **B8.0 unblocked, ~2h, сделать до пилота 11 мая** |
| 3 | **RLS нет на digital_twins/users** — пользователь A теоретически может получить данные пользователя B через прямой DB-доступ (не через Gateway) | низкая | высокий | Interim: Gateway = единственная точка входа + no direct DB access. Полное решение: B4.23 пр.2 dep WP-227 |

---

## 9. Как обновлять этот документ

### VR.R.002 Аудитор — Monthly Close (~1h)

```
Роль: VR.R.002 Аудитор (context isolation, Sonnet)
Триггер: Month Close (первый Пн месяца)
Шаги:
1. Открыть WP-212 context + этот файл
2. Пересчитать §2 (прогресс фаз) — grep [x]/[ ] в WP-212 backlog
3. Обновить §3 (open vulns) — добавить закрытые, добавить новые из STRIDE/ArchGate
4. Обновить §4 (CI coverage) — проверить репо на наличие security.yml
5. Обновить §5 (compliance) — изменилось что-то в WP-186/юр?
6. Добавить строку в §7 (история аудитов)
7. Обновить §6 (inventory) если были ротации или новые сервисы
8. Пересмотреть §8 (топ-3 риска) — остались ли актуальны?
9. Обновить `next_audit` и `updated` в frontmatter
10. Коммит: `docs(WP-212): monthly security posture update YYYY-MM`
```

### Week Close (2 мин, не VR.R.002, встроен в Week Close)

```
Проверить: open_critical_count из §3 > 0?
  Если да → добавить в WeekPlan следующей недели строку для WP-212
  Если нет → ничего
```

### При закрытии задачи WP-212

```
После [x] в WP-212 backlog → обновить % в §2 + если закрыта уязвимость → убрать из §3
```

### При добавлении нового сервиса (ArchGate)

```
1. Добавить сервис в B7.2 STRIDE (новая строка в scope-таблице + per-service анализ)
2. Обновить §4 CI coverage (+1 репо)
3. Добавить секрет/сервис в §6 inventory
4. Пересмотреть §8 топ-3 рисков
```
