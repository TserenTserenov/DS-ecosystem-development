---
title: "Security Posture Dashboard"
type: security-dashboard
wp: WP-212
status: active
created: 2026-05-08
updated: 2026-05-08
next_audit: 2026-06-01 (Month Close июнь, R24 Аудитор)
owner: WP-212
audit_cadence:
  weekly: Week Close — quick check (2 мин, open_critical_count > 0?)
  monthly: Month Close — R24 Аудитор full review (~1h, обновить все секции)
  per_arch: ArchGate §Б — при добавлении нового сервиса (STRIDE + чеклист)
related:
  protocol: DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Identity-and-Access/B7.4-external-audit-checklist.md
  threat_model: DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Identity-and-Access/B7.2-stride-threat-model.md
  pii_map: DS-ecosystem-development/C.IT-Platform/C2.IT-Platform/C2.2.Architecture/Data-Governance/B3.1-pii-field-map.md
---

# Security Posture Dashboard

> **Источник правды:** WP-212 (Программа безопасности продуктов).
> **Обновляется:** автоматически при закрытии задач WP-212, вручную — R24 Аудитор при Month Close.
> **Назначение:** единая точка для быстрой оценки состояния безопасности, подготовки к внешнему аудиту, принятия решений о приоритетах.

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
| Ф2 Секреты | 5 | 4 | 80% | B2.5 OAuth шифрование (dep: Дима + aist_bot) |
| Ф3 Данные пользователей | 9 | 5 | 56% | B3.6 GDPR erasure, B3.9 consent (dep: aist_bot) |
| Ф4 Auth Hardening | 17 | 15 | 88% | B4.23 пр.1 (dep WP-231), B4.23 пр.2 (dep WP-227) |
| Ф5 CI/CD | 6 | 5 | 83% | B5.6 private repos (dep GitHub Pro) |
| Ф6 Backup/DR | 4 | 4 | 100% | ✅ — |
| Ф7 ArchGate | 9 | 6 | 67% | B7.2 review Паша, B7.3.6 доступ Павла |
| Ф8 Compliance | 8 | 0 | 0% | B8.0 ToS+Privacy (unblocked, ~2h) |
| Ф9 Neon RLS roll-out | 7 | 1 | 14% | B9.x dep WP-228 |
| **Итого** | **73** | **48** | **66%** | — |

---

## 3. Открытые уязвимости (по критичности)

> Обновляется R24 Аудитором при каждом аудите. Источник: STRIDE B7.2 + ArchGate §Б + incident log.

| Критичность | Кол-во | Примеры | Дедлайн |
|-------------|--------|---------|---------|
| 🔴 критическая | 2 | B2.5 OAuth tokens plaintext в БД; B4.23 пр.2 RLS на digital_twins/users | dep WP-234/WP-227 |
| 🟡 высокая | 4 | B4.9 Auth events log нет; B7.2 draft (не review); B8.0 ToS/Privacy нет; Variant E (JWT claim) pending Паша | W19-W20 |
| 🟢 средняя | 6 | B3.6 GDPR erasure; B3.7 activity hub bulk sync; B3.9 consent UI; B4.1 API RBAC; B7.4 external audit prep; B9.x RLS roll-out | W20-W21 |
| ⚪ низкая | 4 | B5.5 container scan; FSM concurrency lock; GitHub App scope re-consent; timing side-channel | backlog |
| **Итого** | **16** | — | — |

---

## 4. CI/CD Security Coverage

| Репо | TruffleHog | Dependabot | SAST | Branch Protection | Secret Scan |
|------|-----------|-----------|------|-------------------|-------------|
| aist_bot | ✅ | ✅ | ✅ bandit | ✅ pilot+new-arch | ✅ |
| knowledge-mcp | ✅ | ✅ | ✅ semgrep | ✅ main | ✅ |
| digital-twin-mcp | ✅ | ✅ | ✅ semgrep | ✅ main | ✅ |
| personal-knowledge-mcp | ✅ | ✅ | ✅ semgrep | 🔴 (GitHub Pro) | ✅ |
| gateway-mcp | ✅ | ✅ | ✅ semgrep | 🔴 (GitHub Pro) | ✅ |
| activity-hub | ✅ | ✅ | ✅ bandit | 🔴 (GitHub Pro) | ✅ |
| payment-receiver | ✅ | ✅ | — | 🔴 (GitHub Pro) | ✅ |
| event-gateway | — | ✅ | — | 🔴 (GitHub Pro) | — |

**Coverage score:** 7/8 репо TruffleHog, 8/8 Dependabot, 6/8 SAST, 3/8 Branch Protection.

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

## 6. История аудитов

| Дата | Тип | Аудитор | Итог | Артефакт |
|------|-----|---------|------|---------|
| 2026-04-08 | Первичный внутренний | Claude (Sonnet) | 13 находок инфры + 10 потоков данных | WP-212 §Сводная таблица рисков |
| 2026-04-12 | Ф1 Remediation | Claude (Sonnet) + Паша | Ф1 ✅, Ф4 80% | WP-212 Ф4 |
| 2026-04-14 | Ф2-Ф7 Deep dive | Claude (Sonnet) | 48/65 DONE, sub-agent верификация PASS | WP-212 Handoff 14 апр |
| 2026-04-28 | STRIDE first-pass | Claude (Sonnet) | 8 сервисов охвачено, 6 open questions | B7.2-stride-threat-model.md |
| 2026-05-08 | Статус ревью | R24 Аудитор (Sonnet) | 48/73 66%, 16 open vulns, посture level 1 | этот файл |
| **2026-06-01** | Month Close аудит | **R24 Аудитор** | запланирован | — |

---

## 7. Ключевые риски (топ-3 на сейчас)

| # | Риск | Вероятность | Impact | Митигация |
|---|------|-------------|--------|-----------|
| 1 | **OAuth tokens в plaintext** — утечка БД aist_bot → все GitHub/Google токены пользователей компрометированы | средняя | критический | B2.5 pending Дима. Interim: Neon AES-256 at-rest + сетевая изоляция |
| 2 | **Нет ToS/Privacy** — YooKassa может заблокировать платежи, GDPR жалоба при первом EU-пользователе | низкая | высокий | **B8.0 unblocked, ~2h, сделать до пилота 11 мая** |
| 3 | **RLS нет на digital_twins/users** — пользователь A теоретически может получить данные пользователя B через прямой DB-доступ (не через Gateway) | низкая | высокий | Interim: Gateway = единственная точка входа + no direct DB access. Полное решение: B4.23 пр.2 dep WP-227 |

---

## 8. Как обновлять этот документ

### R24 Аудитор — Monthly Close (~1h)

```
Роль: R24 Аудитор (context isolation, Sonnet)
Триггер: Month Close (первый Пн месяца)
Шаги:
1. Открыть WP-212 context + этот файл
2. Пересчитать §2 (прогресс фаз) — grep [x]/[ ] в WP-212 backlog
3. Обновить §3 (open vulns) — добавить закрытые, добавить новые из STRIDE/ArchGate
4. Обновить §4 (CI coverage) — проверить репо на наличие security.yml
5. Обновить §5 (compliance) — изменилось что-то в WP-186/юр?
6. Добавить строку в §6 (история аудитов)
7. Пересмотреть §7 (топ-3 риска) — остались ли актуальны?
8. Обновить `next_audit` и `updated` в frontmatter
9. Коммит: `docs(WP-212): monthly security posture update YYYY-MM`
```

### Week Close (2 мин, не R24, встроен в Week Close)

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
3. Пересмотреть §7 топ-3 рисков
```
