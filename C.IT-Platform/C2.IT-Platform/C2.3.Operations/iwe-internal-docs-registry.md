---
family: F8
kernel: C
system: C2
role: Operations
audience: platform-team
valid_from: 2026-05-06
status: active
wp: 287
phase: Ф3
note: Реестр существующей технической документации IWE для разработчиков и контрибуторов. Что есть, где лежит, чего нет.
---

# Реестр технической документации IWE

> **Аудитория:** разработчики, контрибуторы, DevOps.
> **Назначение:** быстрый поиск нужного документа. Не замещает source-of-truth — только указывает где они.
> **Обновление:** при добавлении нового значимого артефакта (runbook, ADR, API spec) — добавить строку сюда.

## 1. Архитектура платформы

| Документ | Путь | Что содержит |
|---------|------|-------------|
| DP.ARCH.003 (Digital Twin) | `PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.003-*` | Метамодель Памяти.Derived, структура digital_twins |
| DP.ARCH.004 (Data Architecture) | `PACK-digital-platform/pack/digital-platform/02-domain-entities/` | 12-БД архитектура Neon, классификация данных B7.3 |
| C4 Platform | `C2.2.Architecture/Stack-and-Infrastructure/c4-platform.md` | Диаграмма компонентов платформы |
| Deployment Topology | `C2.2.Architecture/Stack-and-Infrastructure/DP.D.030-deployment-topology.md` | Где что деплоится (CF Workers, tsekh-1, Railway) |
| Deployment Guide | `C2.2.Architecture/Stack-and-Infrastructure/deployment.md` | Как деплоить сервисы |
| MCP Access Model | `C2.2.Architecture/Identity-and-Access/DP.D.031-mcp-access-model.md` | OAuth + JWT, два уровня Gateway (free/paid) |
| ADR-012 JWT verification | `C2.2.Architecture/Identity-and-Access/ADR-IWE-012-mcp-independent-jwt-verification.md` | Независимая JWT-верификация в MCP |
| STRIDE Threat Model | `C2.2.Architecture/Identity-and-Access/B7.2-stride-threat-model.md` | Угрозы безопасности платформы |
| DR/Backup Policy | `C2.2.Architecture/Identity-and-Access/B6.1-backup-dr-policy.md` | Политика резервного копирования |
| Secrets Inventory | `C2.2.Architecture/Identity-and-Access/B2.1-secrets-inventory.md` | Реестр секретов |

## 2. API и MCP Gateway

| Компонент | Репо / Файл | Что содержит |
|-----------|------------|-------------|
| **Aisystant MCP (Gateway)** | `DS-MCP/gateway-mcp/src/index.ts` | Единая точка входа, tool routing, OAuth |
| SC.023 MCP extensibility | `PACK-digital-platform/08-service-clauses/DP.SC.023-mcp-extensibility.md` | Обещание MCP Gateway как расширяемого слоя |
| SC.022 Personal knowledge indexing | `PACK-digital-platform/08-service-clauses/DP.SC.022-personal-knowledge-indexing.md` | Обещание personal_* tools |
| SC.112 Subscription billing | `PACK-digital-platform/08-service-clauses/DP.SC.112-subscription-billing.md` | Gate по подписке в Gateway |
| Knowledge MCP | `DS-MCP/knowledge-mcp/` | knowledge_search, knowledge_get_document |
| Digital Twin MCP | `DS-MCP/digital-twin-mcp/` | dt_read, dt_calc, rcs_current |
| Event Gateway | `DS-MCP/event-gateway/` | Приём и форвардинг domain_event |
| MCP Namespace | `DS-MCP/MCP-NAMESPACE.md` | Реестр всех MCP tools и их namespace |

## 3. Runbooks

| Runbook | Путь | Сценарий |
|---------|------|---------|
| RUNBOOK.001 aist-bot errors | `C2.3.Operations/Runbooks/DP.RUNBOOK.001-aist-bot-errors.md` | Диагностика ошибок бота |
| RUNBOOK.002 L2.5 outbox replay | `C2.3.Operations/Runbooks/DP.RUNBOOK.002-l2.5-outbox-replay.md` | Replay событий из outbox |
| RUNBOOK.003 cascade secret rotation | `C2.3.Operations/Runbooks/DP.RUNBOOK.003-cascade-secret-rotation.md` | Ротация секретов каскадом |
| DR tsekh-1 | `C2.2.Architecture/Identity-and-Access/B6.3-B6.4-dr-runbook-neon-sla.md` | DR для Neon + tsekh-1 |

## 4. IWE-специфичные docs для разработчиков

| Документ | Путь | Что содержит |
|---------|------|-------------|
| FMT-exocortex-template | `FMT-exocortex-template/` | Шаблон IWE для форка пользователем |
| FMT CLAUDE.md | `FMT-exocortex-template/CLAUDE.md` | Правила шаблона, что редактировать/нет |
| Скилл Day Open | `FMT-exocortex-template/.claude/skills/day-open/SKILL.md` | Алгоритм Day Open |
| Скилл personal-guide-start | `FMT-exocortex-template/.claude/skills/personal-guide-start/SKILL.md` | Bootstrap personal-guide репо |
| template-sync.sh | `FMT-exocortex-template/scripts/template-sync.sh` | Синхронизация авторский IWE → FMT |
| update.sh | `FMT-exocortex-template/scripts/update.sh` | Апдейт пользовательского IWE из FMT |
| sync-manifest.yaml | `memory/sync-manifest.yaml` | Реестр drift-пар (источник ↔ производное) |
| Render Портной | `DS-autonomous-agents/scripts/render-pilot-guides.py` | Еженедельный/ежедневный рендер personal-guide |
| Конфиг пилотов | `DS-autonomous-agents/config/pilot-guides.yaml` | Q2 ручной список пилотов |

## 5. Что отсутствует (gap-анализ, Q3+)

| Артефакт | Почему нужен | Когда |
|---------|-------------|-------|
| API reference для MCP Gateway (OpenAPI/MCP spec) | Контрибуторы не знают полный список tools + параметры | Q3+ |
| Runbook: добавить пилота автоматически | Сейчас ручной процесс в pilot-guides.yaml | Q3+ (WP-149 v2) |
| Runbook: роллбэк render-pilot-guides | Нет процедуры откатить упавший render | Q3+ |
| Contributing guide для FMT | Как вносить изменения в шаблон без нарушения L1/L2/L3 | Q3+ |
| Архитектурное ADR: IWE browser vs VS Code | Где граница и почему | WP-287 Ф4 (iwe-browser-setup.md) |

## 6. Ключевые принципы (для новых разработчиков)

- **Fallback Chain:** DS → Pack → Base (SPF → FPF → ZP). Pack = source-of-truth доменного знания.
- **L1/L2/L3:** L1 = платформа (FMT, update.sh). L2 = staging. L3 = авторское (Extensions Gate).
- **Repo-Touch Gate:** первое действие в любом репо → `<repo>/CLAUDE.md`.
- **OwnerIntegrity:** один факт — одно место. Дублирование Pack↔DS = ошибка синхронизации.
- **Incidents:** `C2.3.Operations/Incidents/` — сбои с разбором. Логи остаются в репо сервиса.
