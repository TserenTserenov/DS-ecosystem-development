---
family: F5
kernel: C
system: C2
role: Architecture
status: draft
created: 2026-04-09
target_audience:
  - "Архитектор"
  - "DevOps"
depends_on: [DP.D.031, DP.D.025, DP.ARCH.002]
---

# Data Governance — учёт, доступ, аудит данных в экосистеме

> **Source-of-truth (domain)**: [PACK-digital-platform](../../../../../PACK-digital-platform/) (после завершения исследования)
>
> Сейчас: исследование. Формализованное знание мигрирует в Pack.

## Назначение

Архитектура управления данными в экосистеме: кто что учитывает, кто к чему имеет доступ, кто проверяет. Основана на триаде **учёт–доступ–аудит** (аналог разделения властей для информации).

## Документы

| Документ | Что содержит | Статус |
|----------|-------------|--------|
| [Концепция устройства IWE](iwe-data-architecture-concept.md) | Общая архитектурная картина: данные, домены, агенты, роли. 13 принципов. Триада | draft |
| [Исследование Data Governance](data-governance-research.md) | Госинфраструктура (X-Road, India Stack, СМЭВ) + SOTA ИИ-систем (MCP, Cedar, Mem0). Маппинг на IWE | done |
| *(planned)* Протокол межагентного доступа | Cedar-файл с permissions: типы агентов x домены x операции | — |
| *(planned)* Реестр доменов | Какие домены, MCP-серверы, агенты допущены | — |
| *(planned)* Стандарт межсервисной аутентификации | mTLS + Keto | — |

## Связанные материалы

### Посты

- [#108 Парламент вместо президента: как устроить учёт персональных данных в ИИ-среде](../../../../DS-Knowledge-Index-Tseren/docs/2026/09-апрель/2026-04-09-108-personal-data-accounting-parliament-not-president/108-1-club-2026-04-09.md) — club, draft

### Документы экосистемы

- [MCP Access Model (DP.D.031)](../Identity-and-Access/DP.D.031-mcp-access-model.md) — публичный vs приватный MCP
- [ADR-IWE-008: Identity — Ory ID universal](../System-Implementations/ADR-IWE-008-identity-ory-id-universal.md) — единый ID через Ory
- [Regional-Split/](../Regional-Split/) — разделение контуров РФ/мир: псевдонимизация, триада при двух контурах (WP-215)

### Внешние источники

| Источник | Что взяли |
|----------|----------|
| ФЦП «Электронная Россия» (elrussia.ru, 2006) | Триада учёт–доступ–аудит |
| Эстония X-Road | Centralize trust / decentralize data, Security Server pattern, 3 типа логов |
| Индия DEPA | Consent as architectural primitive, Consent Artifact |
| Сингапур MyInfo | Infrastructure-first, tell-us-once |
| ЕС GAIA-X / eIDAS v2 | Data sovereignty, self-sovereign identity, секторальные домены |
| Россия СМЭВ | Витрины данных, антипаттерн централизованной шины |
| NHS NPfIT (UK) | Антипаттерн: централизованная суперсистема = 10 млрд потерь |
| AWS Bedrock AgentCore (Cedar) | Declarative policies, formal verification |
| Ory Keto (Zanzibar) | ReBAC — relation-based access control |
| Mem0 | Hybrid memory (vector + graph + key-value) |

## Триада

| Институт | Что делает | Аналог в IWE |
|----------|-----------|--------------|
| **Учёт** | Фиксирует факты в своей зоне | Pack-репозиторий (source-of-truth домена) |
| **Доступ** | Регулирует кто что видит | CLAUDE.md + протоколы + SC + Gates + MCP permissions |
| **Аудит** | Проверяет соблюдение правил | Верификация (context isolation), логирование |

## Реестр объектов внимания

| Объект | Описание | Статус | Принцип |
|--------|----------|--------|---------|
| Концепция устройства IWE | Общая архитектура: 3 слоя, 13 принципов | draft | все |
| Протокол межагентного доступа | Какой агент к каким данным имеет право | planned | P3, P4, P5 |
| Межсервисная аутентификация | Как сервисы подтверждают друг другу, что «свои» | исследование | P2 |
| MCP Access Model | Публичный vs приватный MCP | active (DP.D.031) | P2, P12 |
| RLS (Row-Level Security) | Фильтрация данных по user_id | active | P3 |
| Consent layer | Механизм consent (что, кому, зачем, срок) | не реализовано | P3 |
| Audit trail | Логирование кто-кого-когда вызвал | не реализовано | P9 |
| Реестр доменов | Какие домены, MCP-серверы, допущенные агенты | начальный (MAP.002) | P1, P13 |
