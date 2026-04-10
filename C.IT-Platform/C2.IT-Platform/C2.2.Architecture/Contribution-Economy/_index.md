---
family: F5
kernel: C
system: C2
role: Architecture
status: draft
created: 2026-04-09
source_of_truth: PACK-digital-platform/pack/digital-platform/08-service-clauses/DP.SC.105-reputation-economy.md
depends_on: [WP-121, WP-215, WP-109, WP-183]
---

# Экономика вклада (Contribution Economy)

> **Source-of-truth (домен):** [DP.SC.105 — Экономика вклада](../../../../../PACK-digital-platform/pack/digital-platform/08-service-clauses/DP.SC.105-reputation-economy.md)
>
> Здесь — архитектурная проработка: как реализовать систему баллов на платформе. Доменные правила (что за что начисляется) — в Pack.

## Назначение

Система начисления баллов за вклад участников в сообщество. Баллы = нефинансовая метрика, конвертируемая в скидки на сервисы платформы. Единая для всех участников независимо от юрисдикции и контура оплаты.

## Документы

| # | Документ | Содержание |
|---|----------|-----------|
| 01 | [Доменная модель](01-domain-model.md) | Events → Rules → Transactions → Balances. Терминология, инварианты, replay |
| 02 | [Архитектура двух контуров](02-cross-region-architecture.md) | Общие баллы при разделении РФ/мир. Варианты, юридическая модель, эволюция |
| 03 | [Множители и ограничения](03-multipliers-and-caps.md) | Три оси множителей, caps, формула, систематичность. Калибровка |
| 04 | [Карта интеграций](04-integration-map.md) | Кто пишет, кто читает, кто владеет. Activity Hub, CRM, Billing, Ory, бот |

## Связи

| Система | Связь | Документ |
|---------|-------|----------|
| Activity Hub (WP-109) | Источник событий (user_events) | [ADR-005](../System-Implementations/ADR-IWE-005-ingest-event-activity-hub.md) |
| CRM + Billing (WP-183) | Списание баллов (type=spent) | WP-183 context |
| Ory Identity (WP-187) | ory_id = идентификатор участника | [ADR-008](../System-Implementations/ADR-IWE-008-identity-ory-id-universal.md) |
| Разделение РФ/мир (WP-215) | Общие баллы при разделённой инфраструктуре | [02-cross-region](02-cross-region-architecture.md), [Regional-Split/ (B3.1.Meaning)](../../../../B.Aisystant-Ecosystem/B3.Ecosystem-Builder/B3.1.Meaning/Regional-Split/) |
| ЦД (DP.ARCH.003) | Квалификация из ЦД → множитель баллов | Pack |
| Бот | /points — отображение баланса | WP-121 Ф3 |

## Принципы (из SC.105 + WP-121)

1. **Events = неизменяемые факты** (append-only user_events)
2. **Баллы = вычисляемая проекция** из events по rules
3. **Пересчёт = replay** (прогнать rules по всем events заново)
4. **Idempotent** — один event = максимум одно начисление (UNIQUE event_id)
5. **Баллы ≠ деньги** — нефинансовая метрика вклада в сообщество
6. **Квалификация ≠ тир** — множитель по степени квалификации МИМ (8 степеней: Ученик → Общественный деятель), не по уровню подписки
7. **Бесплатная подписка за вклад допустима** — Мастер+ при ежедневной активности может покрыть 100%+ подписки

## Калибровка (9 апр 2026)

Проведена по реальным данным Activity Hub: 66 934 events, 102 users, период 2020-2026. Результаты и сводная таблица по 8 квалификациям — в [03-multipliers-and-caps.md](03-multipliers-and-caps.md) §4.

---

*Создано: 2026-04-09. WP: 121, 215.*
