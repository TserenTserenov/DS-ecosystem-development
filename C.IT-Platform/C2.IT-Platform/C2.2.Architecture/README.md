# C2.2. IT-Platform — Architecture

> **Source-of-truth (domain)**: [PACK-digital-platform](../../../../PACK-digital-platform/)
>
> Реализационные решения ИТ-платформы. Здесь живёт то, что зависит от конкретных вендоров, фреймворков, инфраструктуры.

## Подразделы

| Папка | Содержит |
|-------|----------|
| [Stack-and-Infrastructure](Stack-and-Infrastructure/) | Топология деплоя, стек, circuit breaker |
| [Data-Stores](Data-Stores/) | Neon, PostgreSQL, pgvector — схемы и конфигурации |
| [Data-Governance](Data-Governance/) | Учёт, доступ, аудит данных. Триада, межсервисная аутентификация, протокол межагентного доступа |
| [Identity-and-Access](Identity-and-Access/) | Модели доступа, Ory, RLS |
| Regional-Split → [B3.1.Meaning/Regional-Split/](../../../B.Aisystant-Ecosystem/B3.Ecosystem-Builder/B3.1.Meaning/Regional-Split/) | Разделение контуров Россия/мир: стратегическая концепция, compliance, инвесторы (WP-215). Перенесено в B3.1.Meaning (F3) 10 апр — это стратегические решения для инвесторов/регуляторов, не техническая инфраструктура. |
| [System-Implementations](System-Implementations/) | ADR, реестр детерминированных систем |

## HD #29 — Pack vs DS

**Тест:** «Заменили вендора/фреймворк — утверждение стало ложным? Да → тут (DS). Нет → в Pack.»
