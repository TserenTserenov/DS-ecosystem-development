# Реестр репозиториев экосистемы

> **Source-of-truth** для списка репозиториев экосистемы развития интеллекта.
> Обновляется при создании/удалении репозиториев.

## Типы репозиториев (5 семей верхнего уровня)

| Тип | Подтип | Что содержит | Source-of-truth | Кто создаёт |
|-----|--------|-------------|-----------------|-------------|
| **Base** | Принципы | ZP, FPF, SPF — принципы и фреймворки корректности | Да | Платформа |
| **Base** | Форматы | FMT-* — протоколы структуры репо | Да (для формата) | Платформа |
| **Pack** | — | Паспорт предметной области (вторые принципы) | Да | Пользователь |
| **DS** | instrument | Код, боты, агенты, MCP | Нет | Пользователь |
| **DS** | governance | Планы, реестры, координация | Нет | Пользователь |
| **DS** | surface | Курсы, гайды, публикации | Нет | Пользователь |
| **PD** | — | Личные данные пользователя (типы 2.1-2.4), без кода | Нет (данные, не знание) | Пользователь |
| **MC** | — | Машинные данные агент-для-агента (диалоги, служебные логи) | Нет | Агенты (по поручению пользователя) |

> Base = платформа выдаёт. Pack и DS = пользователь создаёт.
> Pack = вторые принципы. DS = третьи принципы. Подробно: `ZP/README.md`
> **PD и MC** (решение 18.08.2026, WP-526 Ф5) — не подтипы DS, параллельные семьи; хранят данные, а не знание. Правила именования → `PACK-digital-platform/.../DP.KR.001-knowledge-routing.md §3.4`.

---

## 4D-классификация (сводная таблица)

> 4 измерения: **Тип** / **Система (SoI)** / **Содержание** / **Для кого**

| # | Репозиторий | Тип | Система | Содержание | Для кого | SoT | Статус |
|---|-------------|-----|---------|------------|----------|-----|--------|
| 0 | [ZP](https://github.com/TserenTserenov/ZP) | Base/Принципы | cross-cutting | text-description | public | yes | Active |
| 1 | [FPF](https://github.com/ailev/FPF) | Base/Принципы | cross-cutting | text-description | public | yes | External |
| 2 | [SPF](https://github.com/TserenTserenov/SPF) | Base/Принципы | cross-cutting | text-description | public | yes | Active |
| 3 | [FMT-S2R](https://github.com/TserenTserenov/FMT-S2R) | Base/Форматы | cross-cutting | text-description | public | yes | Active |
| 14 | [FMT-exocortex-template](https://github.com/TserenTserenov/FMT-exocortex-template) | Base/Форматы | cross-cutting | text-description | public | yes | Active |
| 4 | [PACK-personal](https://github.com/aisystant/PACK-personal) | Pack | Созидатель | text-description | team | yes | Active |
| 5 | [PACK-ecosystem](https://github.com/TserenTserenov/PACK-ecosystem) | Pack | Экосистема | text-description | team | yes | Active |
| 6 | [PACK-digital-platform](https://github.com/TserenTserenov/PACK-digital-platform) | Pack | ИТ-платформа | text-description | team | yes | Active |
| 20 | [PACK-MIM](https://github.com/TserenTserenov/PACK-MIM) | Pack | МИМ (мастерская) | text-description | team | yes | Active |
| ~~24~~ | ~~[PACK-education](https://github.com/TserenTserenov/PACK-education)~~ | ~~Pack~~ | ~~Методика обучения~~ | ~~—~~ | ~~—~~ | ~~—~~ | Archived → PACK-MIM (WP-154) |
| 25 | [PACK-verification](https://github.com/TserenTserenov/PACK-verification) | Pack | Верификация и приёмка | text-description | team | yes | Active |
| 27 | [PACK-autonomous-agents](https://github.com/TserenTserenov/PACK-autonomous-agents) | Pack | Автономные агенты | text-description | team | yes | Active |
| — | ~~DS-twin~~ | — | — | — | — | — | Archived → digital-twin-mcp (#18) |
| 9 | [DS-Knowledge-Index-Tseren](https://github.com/TserenTserenov/DS-Knowledge-Index-Tseren) | DS/instrument | Созидатель | code | personal | no | Active |
| 10 | [DS-ecosystem-development](https://github.com/aisystant/DS-ecosystem-development) | DS/governance | Экосистема | text-governance | team | no | Active |
| 11 | [DS-my-strategy](https://github.com/TserenTserenov/DS-my-strategy) | DS/governance | Созидатель | text-governance | personal | no | Active |
| 12 | [docs](https://github.com/aisystant/docs) | DS/surface | Экосистема | text-publication | public | no | Active |
| 13 | [DS-marathon-v2-tseren](https://github.com/TserenTserenov/DS-marathon-v2-tseren) | DS/surface | Экосистема | text-publication | team | no | Active |
| 23 | [DS-principles-curriculum](https://github.com/aisystant/DS-principles-curriculum) | DS/surface | Экосистема | text-publication | team | no | Active |
| 15 | [DS-ai-systems](https://github.com/TserenTserenov/DS-ai-systems) | DS/instrument | ИТ-платформа | code | personal | no | Active |
| 18 | [digital-twin-mcp](https://github.com/aisystant/digital-twin-mcp) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 19 | [aist_bot_newarchitecture](https://github.com/aisystant/aist_bot_newarchitecture) | DS/instrument | Бот Aist | code | team | no | Active |
| 21 | [aisystant](https://github.com/aisystant/aisystant) | DS/instrument | Экосистема | code | team | no | External |
| 22 | [SystemsSchool_bot](https://github.com/aisystant/SystemsSchool_bot) | DS/instrument | Экосистема | code | team | no | External |
| 26 | [activity-hub](https://github.com/aisystant/activity-hub) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 28 | [DS-autonomous-agents](https://github.com/TserenTserenov/DS-autonomous-agents) | DS/instrument | Автономные агенты | code | personal | no | Active |
| 30 | [DS-agent-workspace](https://github.com/TserenTserenov/DS-agent-workspace) | DS/governance | Автономные агенты | agent-outputs | personal | no | Active |
| 29 | [knowledge-mcp](https://github.com/aisystant/knowledge-mcp) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 31 | [guides-mcp](https://github.com/aisystant/guides-mcp) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 32 | [fsm-mcp](https://github.com/aisystant/fsm-mcp) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 33 | [gateway-mcp](https://github.com/aisystant/gateway-mcp) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 34 | [payment-registry](https://github.com/aisystant/payment-registry) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 35 | [payment-receiver](https://github.com/aisystant/payment-receiver) | DS/instrument | ИТ-платформа | code | team | no | Active |
| 36 | [iwe-server-config](https://github.com/TserenTserenov/iwe-server-config) | DS/instrument | ИТ-платформа | code | personal | no | Active |
| 37 | [DS-iwe-wp-panel](https://github.com/TserenTserenov/DS-iwe-wp-panel) | DS/instrument | Экзокортекс IWE | code (VS Code extension) | personal | no | Active |
| 38 | [FMT-brand-template](https://github.com/TserenTserenov/FMT-brand-template) | Base/Формат | Личный бренд | template | public | yes (для формата) | Active |
| 39 | [PD-metrics](https://github.com/TserenTserenov/PD-metrics) | PD | Созидатель | personal-data (питание/измерения/здоровье) | personal | no | Active (переименован из DS-metrics — WP-526 Этап 1, подтверждено `gh repo view` 28.08) |
| 40 | [MC-sessions](https://github.com/TserenTserenov/MC-sessions) | MC | cross-cutting (агенты) | agent-dialogs | personal | no | Active (перенос `sessions/` из DS-my-strategy выполнен 29.08 — WP-526 Ф2: резолвер путей, pre-commit блок на старое место) |
| 41 | [PD-persona](https://github.com/TserenTserenov/PD-persona) | PD | Созидатель | personal-data (personal/, Lifework/, мастерства) | personal | no | Active (создан 29.08 — WP-526 Ф5: personal/ + Lifework/ переехали из DS-my-strategy с историей, 52 коммита) |
| 42 | [PD-dashboard](https://github.com/TserenTserenov/PD-dashboard) | PD | Созидатель | code + personal-data (дашборд рабочих продуктов, снимки WP-417) | personal | no | Active (создан 01.09 — WP-417, ночной writer пишет ежедневный снимок) |
| 43 | [DS-piano](https://github.com/TserenTserenov/DS-piano) | DS/instrument | Созидатель | code + personal-data (трекер практики фортепиано) | personal | no | Active (создан 01.09 через `/repo-new` — WP-527 Ф3 живая обкатка, связано с WP-558) |
| 44 | [DS-Tseren-Brand](https://github.com/TserenTserenov/DS-Tseren-Brand) | DS/surface | Личный бренд | text-description (факты/позиционирование/голос для публикаций) | personal | no | Active |
| 45 | [DS-creator-development](https://github.com/TserenTserenov/DS-creator-development) | DS/surface | Созидатель | text-publication (программа личного развития, SC.020) | personal | no | Active |
| 46 | [DS-iwe-session-trigger](https://github.com/TserenTserenov/DS-iwe-session-trigger) | DS/instrument | Экзокортекс IWE | code (VS Code extension, WP-359) | personal | no | Active |
| 47 | [DS-platform-infra](https://github.com/TserenTserenov/DS-platform-infra) | DS/instrument | ИТ-платформа | code (Railway: LiteLLM прокси + шлюз авторизации ботов) | team | no | Active |
| 48 | [DS-strategist-agent](https://github.com/TserenTserenov/DS-strategist-agent) | DS/instrument | Автономные агенты | code (запуск агента Стратег — скрипты/промпты/расписание) | personal | no | Active |
| 49 | [DS-wp-sandbox](https://github.com/TserenTserenov/DS-wp-sandbox) | DS/instrument | ИТ-платформа | code (изолированная песочница проверки создания РП через MCP) | personal | no | Active |
| 50 | [PACK-rhetoric](https://github.com/TserenTserenov/PACK-rhetoric) | Pack | Риторика (кросс-доменная) | text-description | team | yes | Active |
| 51 | [PACK-systems-art](https://github.com/TserenTserenov/PACK-systems-art) | Pack | Системное искусство | text-description | team | yes | Active |
| 52 | [iwe-local-config](https://github.com/TserenTserenov/iwe-local-config) | DS/instrument | ИТ-платформа | code (личный конфиг IWE-агента на Mac — хуки/скрипты/расширения) | personal | no | Active |
| 53 | [iwe-guide-web](https://github.com/TserenTserenov/iwe-guide-web) | DS/instrument | Экзокортекс IWE | code (читалка персональных/универсальных руководств, Railway) | personal | no | Active |
| 54 | [aisystant-com](https://github.com/aisystant/aisystant-com) | DS/surface | Экосистема | text-publication (публичный сайт Aisystant, VitePress) | team | no | Active |
| 55 | [checklist-mcp](https://github.com/aisystant/checklist-mcp) | DS/instrument | ИТ-платформа | code (MCP2.0 read-model чек-листа участника, WP-522 §3в) | team | no | Active |
| 56 | [guide-kit](https://github.com/iwesys/guide-kit) | DS/instrument | Экзокортекс IWE | code (открытый проект, MIT, «свои заметки + свой ИИ-ассистент») | public | no | Active |
| 57 | [iwe-dev](https://github.com/iwesys/iwe-dev) | DS/governance | Экзокортекс IWE | text-governance (координация команды развития IWE) | team | no | Active |
| 58 | [iwe-local-gateway](https://github.com/iwesys/iwe-local-gateway) | DS/instrument | ИТ-платформа | code (локальный шлюз координации многоагентных сессий) | team | no | Active |
| 59 | [iwe-translation-engine](https://github.com/iwesys/iwe-translation-engine) | DS/instrument | ИТ-платформа | code (RU→EN проекция с глоссарием) | team | no | Active |
| 60 | [bridge-2-events-poller](https://github.com/TserenTserenov/bridge-2-events-poller) | DS/instrument | ИТ-платформа | code (WP-268 T4: чтение событий LMS aisystant → event-gateway) | personal | no | Active |
| 61 | [audit-timestamps](https://github.com/TserenTserenov/audit-timestamps) | DS/instrument | ИТ-платформа | code (WP-455: off-DB бэкап Bitcoin-anchor доказательств хэш-цепочки) | personal | no | Active |
| — | ~~DS-aist-bot~~ | — | — | — | — | — | Archived → aist_bot_newarchitecture |
| — | ~~DS-synchronizer~~ | — | — | — | — | — | Archived → DS-ai-systems |
| — | ~~DS-fixer-agent~~ | — | — | — | — | — | Archived → DS-ai-systems |
| — | ~~DS-pulse-agent~~ | — | — | — | — | — | Archived → DS-ai-systems |

---

## По типам (детали)

### Base/Принципы

| Репозиторий | Роль | Владелец |
|-------------|------|----------|
| [ZP](https://github.com/TserenTserenov/ZP) | Zeroth Principles (6 мета-ограничений + карта иерархии 0→1→2→3) | TserenTserenov |
| [FPF](https://github.com/ailev/FPF) | First Principles Framework | ailev |
| [SPF](https://github.com/TserenTserenov/SPF) | Second Principles Framework | TserenTserenov |

### Base/Форматы

| Репозиторий | Роль | Владелец |
|-------------|------|----------|
| [FMT-S2R](https://github.com/TserenTserenov/FMT-S2R) | Structured Second-level Repository | TserenTserenov |
| [FMT-exocortex-template](https://github.com/TserenTserenov/FMT-exocortex-template) | Exocortex template (fork & deploy) | TserenTserenov |

### Pack (Source-of-truth)

| Репозиторий | Область | Upstream | Владелец |
|-------------|---------|----------|----------|
| [PACK-personal](https://github.com/aisystant/PACK-personal) | Созидатель (персональное развитие) | SPF, FPF | aisystant |
| [PACK-ecosystem](https://github.com/TserenTserenov/PACK-ecosystem) | Экосистема развития интеллекта (чёрный ящик + подсистемы) | SPF, FPF | TserenTserenov |
| [PACK-digital-platform](https://github.com/TserenTserenov/PACK-digital-platform) | ИТ-платформа и цифровой двойник | SPF, FPF, PACK-personal | TserenTserenov |
| [PACK-MIM](https://github.com/TserenTserenov/PACK-MIM) | Мастерская: форматы, программы, организация развития | SPF, FPF | TserenTserenov |
| ~~[PACK-education](https://github.com/TserenTserenov/PACK-education)~~ | ~~Archived → PACK-MIM (WP-154). Методика обучения расформирована в MIM.~~ | ~~—~~ | ~~—~~ |
| [PACK-verification](https://github.com/TserenTserenov/PACK-verification) | Верификация и приёмка: методы проверки, эталоны, критерии приёмки (трансдоменный) | SPF, FPF | TserenTserenov |
| [PACK-agent-rules](https://github.com/TserenTserenov/PACK-agent-rules) | Правила работы агента Claude в IWE: реестр AR.NNN с frontmatter, conflicts, revision-flow (трансдоменный, runtime-managed) | SPF, FPF | TserenTserenov |
| [PACK-rhetoric](https://github.com/TserenTserenov/PACK-rhetoric) | Библиотека риторических приёмов IWE: кейсы, аналогии, метафоры для руководств и постов (трансдоменный) | SPF, FPF | TserenTserenov |
| [PACK-systems-art](https://github.com/TserenTserenov/PACK-systems-art) | Системное искусство (SA.*) | SPF, FPF | TserenTserenov |

### DS/instrument

| Репозиторий | Назначение | Upstream pack | Владелец |
|-------------|------------|---------------|----------|
| [DS-Knowledge-Index-Tseren](https://github.com/TserenTserenov/DS-Knowledge-Index-Tseren) | Персональный индекс знаний + публичные посты (`posts/`) | PACK-personal | TserenTserenov |
| [DS-ai-systems](https://github.com/TserenTserenov/DS-ai-systems) | Монорепо ИИ-систем (7 систем: стратег, экстрактор, синхронизатор, наладчик, статистик, оценщик, шаблонизатор) | PACK-digital-platform, PACK-personal | TserenTserenov |
| [digital-twin-mcp](https://github.com/aisystant/digital-twin-mcp) | MCP-сервер цифрового двойника | PACK-digital-platform, PACK-personal | aisystant |
| [aist_bot_newarchitecture](https://github.com/aisystant/aist_bot_newarchitecture) | Telegram-бот (new architecture, State Machine) | PACK-personal | aisystant |
| [aisystant](https://github.com/aisystant/aisystant) | LMS Aisystant (SYS.004) | PACK-ecosystem | aisystant (external) |
| [SystemsSchool_bot](https://github.com/aisystant/SystemsSchool_bot) | Telegram-бот стажировок и расписания | PACK-ecosystem | aisystant (external) |
| [activity-hub](https://github.com/aisystant/activity-hub) | Единая точка записи событий в ЦД (LMS, бот, клуб, IWE) | PACK-digital-platform | aisystant |
| [knowledge-mcp](https://github.com/aisystant/knowledge-mcp) | MCP-сервер поиска по знаниям (Pack, DS, FMT) | PACK-digital-platform | aisystant |
| [guides-mcp](https://github.com/aisystant/guides-mcp) | MCP-сервер руководств и гайдов | PACK-digital-platform | aisystant |
| [fsm-mcp](https://github.com/aisystant/fsm-mcp) | MCP-сервер конечных автоматов | PACK-digital-platform | aisystant |
| [DS-autonomous-agents](https://github.com/TserenTserenov/DS-autonomous-agents) | Код автономных агентов (промпты, dispatcher, trajectory cache) | PACK-autonomous-agents, PACK-digital-platform | TserenTserenov |
| [neon-migrations](https://github.com/TserenTserenov/neon-migrations) | DDL + seeds для 9 БД MVP-greenfield (WP-253 Ф9.1, создан 24 апр 2026) | PACK-digital-platform | TserenTserenov |
| event-gateway *(pending push)* | CF Worker: приём событий Observed → Neon (WP-253 Ф9.2 skeleton, 24 апр 2026) | PACK-digital-platform | TserenTserenov |
| [rewards-projection-worker](https://github.com/aisystant/rewards-projection-worker) ⛔ **decommissioned 2026-05-17** | Python asyncpg LISTEN/NOTIFY: rewards Derived projection (WP-253 Ф9.3, decommission'd WP-311 Ф-Close — функционал в `multi-domain-projection-worker` в `attractive-optimism`) | PACK-digital-platform | TserenTserenov |
| [DS-personal-guide](https://github.com/TserenTserenov/DS-personal-guide) | Персональное руководство ЛР (переименован из `personal-guide` — плоское имя больше не используется; один на пилота, WP-245 Ф28.5) | PACK-personal | TserenTserenov |
| [iwe-server-config](https://github.com/TserenTserenov/iwe-server-config) | NixOS-конфигурация сервера «Цех» tsekh-1 (WP-138, реактивирован 28 апр 2026) | PACK-digital-platform | TserenTserenov |
| [iwe-local-config](https://github.com/TserenTserenov/iwe-local-config) | Личная конфигурация IWE-агента на Mac (хуки, скрипты, расширения) — локальная пара к `iwe-server-config` | PACK-digital-platform | TserenTserenov |
| [DS-piano](https://github.com/TserenTserenov/DS-piano) | Код трекера практики фортепиано + данные о практике (WP-558, создан 01.09) | — | TserenTserenov |
| [DS-iwe-session-trigger](https://github.com/TserenTserenov/DS-iwe-session-trigger) | VS Code extension: следит за SESSION-*.md и запускает Claude Code (WP-359) | — | TserenTserenov |
| [DS-strategist-agent](https://github.com/TserenTserenov/DS-strategist-agent) | Запуск агента Стратег (DP.AGENT.012) — скрипты, промпты, расписание | PACK-digital-platform | TserenTserenov |
| [DS-wp-sandbox](https://github.com/TserenTserenov/DS-wp-sandbox) | Изолированная песочница для проверки создания РП через MCP | — | TserenTserenov |
| [DS-platform-infra](https://github.com/TserenTserenov/DS-platform-infra) | Railway-инфраструктура: LiteLLM прокси + шлюз авторизации ботов | PACK-digital-platform | TserenTserenov |
| [bridge-2-events-poller](https://github.com/TserenTserenov/bridge-2-events-poller) | Чтение событий LMS aisystant → event-gateway (WP-268 T4, read-only legacy reader) | PACK-digital-platform | TserenTserenov |
| [audit-timestamps](https://github.com/TserenTserenov/audit-timestamps) | Off-DB бэкап Bitcoin-anchor доказательств хэш-цепочки событий (WP-455) | PACK-digital-platform | TserenTserenov |
| [iwe-guide-web](https://github.com/TserenTserenov/iwe-guide-web) | Читалка персональных/универсальных руководств (Railway iwe-guide/web) | PACK-personal | TserenTserenov |
| [checklist-mcp](https://github.com/aisystant/checklist-mcp) | MCP2.0 read-model чек-листа участника экосистемы (WP-522 §3в) | PACK-digital-platform | aisystant |
| [guide-kit](https://github.com/iwesys/guide-kit) | Открытый проект (MIT): свои заметки + свой ИИ-ассистент → персональное руководство | PACK-personal | iwesys |
| [iwe-local-gateway](https://github.com/iwesys/iwe-local-gateway) | Локальный шлюз координации многоагентных сессий (файловые локи, статусы напарников) | PACK-digital-platform | iwesys |
| [iwe-translation-engine](https://github.com/iwesys/iwe-translation-engine) | Проекция RU→EN с глоссарием понятий | PACK-digital-platform | iwesys |

### DS/governance

| Репозиторий | Назначение | Upstream packs | Владелец |
|-------------|------------|----------------|----------|
| [DS-ecosystem-development](https://github.com/aisystant/DS-ecosystem-development) | Координация экосистемы | PACK-ecosystem, PACK-personal, PACK-digital-platform | aisystant |
| [DS-my-strategy](https://github.com/TserenTserenov/DS-my-strategy) | Личное стратегирование (HUB агента Стратег) | PACK-personal, PACK-digital-platform | TserenTserenov |
| [DS-agent-workspace](https://github.com/TserenTserenov/DS-agent-workspace) | Шина данных автономных агентов (результаты, черновики, отчёты) | PACK-autonomous-agents, PACK-digital-platform | TserenTserenov |
| [iwe-dev](https://github.com/iwesys/iwe-dev) | Координация команды развития IWE: табло, бэклог, встречи, решения, гайд | PACK-digital-platform | iwesys |

### DS/surface

| Репозиторий | Назначение | Upstream pack | Владелец |
|-------------|------------|---------------|----------|
| [docs](https://github.com/aisystant/docs) | VitePress документация | PACK-personal, PACK-ecosystem | aisystant |
| [DS-marathon-v2-tseren](https://github.com/TserenTserenov/DS-marathon-v2-tseren) | Программа марафона v2 | PACK-personal, PACK-ecosystem | TserenTserenov |
| [DS-principles-curriculum](https://github.com/aisystant/DS-principles-curriculum) | Программа обучения принципам (FPF ячейки) | PACK-personal, PACK-ecosystem | aisystant |
| [aisystant-com](https://github.com/aisystant/aisystant-com) | Публичный сайт Aisystant (VitePress) | PACK-ecosystem | aisystant |
| [DS-Tseren-Brand](https://github.com/TserenTserenov/DS-Tseren-Brand) | База знаний о Церене Церенове: факты, позиционирование, голос для публикаций | PACK-personal | TserenTserenov |
| [DS-creator-development](https://github.com/TserenTserenov/DS-creator-development) | Программа личного развития — руководство по IWE (SC.020) | PACK-personal | TserenTserenov |

### PD (личные данные)

| Репозиторий | Назначение | Статус | Владелец |
|-------------|------------|--------|----------|
| [PD-metrics](https://github.com/TserenTserenov/PD-metrics) | Питание, измерения, здоровье (тип 2.2) | Active | TserenTserenov |
| [PD-persona](https://github.com/TserenTserenov/PD-persona) | Личное: personal/, Lifework/, мастерства (masteries.yaml) | Active (создан 29.08, WP-526 Ф5) | TserenTserenov |

### MC (машинное — агент-для-агента)

| Репозиторий | Назначение | Статус | Владелец |
|-------------|------------|--------|----------|
| [MC-sessions](https://github.com/TserenTserenov/MC-sessions) | Диалоги с агентами (переехали из `DS-my-strategy/sessions/` 29.08) | Active — перенос выполнен (WP-526 Ф2) | TserenTserenov |

---

## Находки полной проверки 03.09.2026 (РП-526) — не добавлены в реестр, решение за пилотом

Полная сверка всех репозиториев аккаунта `TserenTserenov` (51 шт.) + локальных клонов `~/IWE` против этого реестра. Ниже — то, что реестр не покрывал и что не вписано выше как «Active», потому что назначение или судьба не установлены агентом однозначно.

**Удалено пилотом 03.09 с GitHub** (подтверждено `gh repo view`): `DS-my-strategy-dashboard` (репозиторий-стрей-дубль `DS-my-strategy`, создан 30.08, один push — самостоятельный объект на GitHub, не тот же самое, что локальная папка ниже), `desktop-tutorial` (обучающий репозиторий GitHub Desktop, к IWE не относится), `srt-template1` (отдельный проект «Planora» на методе SRT, не структура IWE), три тестовых `DS-test-wp514-*` (сами себя описывали «удалить после проверки»). `~/IWE/srt-template1` (локальный клон, осиротел) тоже убран.

**Живая инфраструктура — НЕ удалять** (первичный вывод «пустое описание» был ошибочным, содержимое проверено):
| Репозиторий | Что это на самом деле |
|-------------|------------------------|
| [hetzner-backstage](https://github.com/TserenTserenov/hetzner-backstage) | Живой выделенный сервер Hetzner (PostgreSQL+pgvector, restic-бэкап 12 баз Neon в Backblaze B2, systemd-таймеры IWE) — этот репозиторий единственный источник для пересборки сервера при переустановке ОС (WP-138 Ф0) |
| [iwe-server](https://github.com/TserenTserenov/iwe-server) | Контролёр развития (WP-346, R2 Onboarding) — systemd-таймер на «Цехе», 3 раза в день опрашивает подключённых участников и шлёт напоминания через бота; живой продовый код |

Архивные (подтверждено `gh repo view`, без действий): `DS-evaluator-agent`, `DS-exocortex-setup-agent`, `DS-extractor-agent`, `tailor-mcp`.

**Разгадка «клона, который не удаляется» (03.09) — это не баг сессий, это работающий механизм с несчастливым именем.** Локальная папка `~/IWE/DS-my-strategy-dashboard` (не репозиторий с GitHub из абзаца выше — тёзка) каждый раз пересоздавалась заново после удаления, потому что её пересоздаёт `DS-iwe-wp-panel/scripts/sync-dashboard-mirror.sh` — задача `com.iwe.wp-dashboard-main-sync` (launchd), тикает раз в 5 минут. Назначение: держать для VS Code-панели (расширение `DS-iwe-wp-panel`) стабильный, всегда-на-main снимок `DS-my-strategy` — рабочая копия слишком часто грязная (параллельные сессии), панели нужен чистый источник. Пойман живьём (процесс `git clone` с PPID этого скрипта) через 3 минуты наблюдения. **Побочный ущерб:** удаление папки (эта сессия сама и посоветовала его сделать — ошибка) столкнуло следующий тик скрипта в гонку — 10 параллельных `git clone` без блокировки испортили ссылки (`HEAD` указывал в никуда), задача переставала успешно синхронизироваться. **Исправлено** ([commit `2c9076e`](https://github.com/TserenTserenov/DS-iwe-wp-panel/commit/2c9076e)): добавлена блокировка (`flock`, тот же приём, что уже используется у сторожа на «Цехе») и самовосстановление при испорченных ссылках; мирор пересоздан и синхронизируется штатно. **Переименовано в тот же день ([commit `fda20c5`](https://github.com/TserenTserenov/DS-iwe-wp-panel/commit/fda20c5)):** мирор перенесён под `~/IWE/.iwe-runtime/dashboard-mirror` — рядом с семафорами сессий и изолированными worktree, где ничей sweep репозиториев больше не споткнётся об него. Путь по умолчанию поправлен и в скрипте синхронизации, и в коде расширения; уже установленная версия расширения (0.1.34) подхватила новый путь без пересборки через `~/IWE/.vscode/settings.json` (`iweWpPanel.sourceRoot`). Проверено: реестр РП и inbox на новом месте читаются, синхронизация идёт штатно.

---

## Граф зависимостей

```
ZP (Base/Принципы, Level 0)
  │
  └──▶ FPF (Base/Принципы, Level 1)
        │
        └──▶ SPF (Base/Принципы, Level 2)
        │
        ├──▶ PACK-personal (Pack: Созидатель)
        │     │
        │     ├──▶ aist_bot_newarchitecture (DS/instrument)
        │     ├──▶ DS-Knowledge-Index-Tseren (DS/instrument)
        │     ├──▶ docs (DS/surface)
        │     └──▶ DS-marathon-v2-tseren (DS/surface)
        │
        ├──▶ PACK-MIM (Pack: Мастерская)
        │     │
        │     └──▶ DS-ecosystem-development (DS/governance)
        │
        │     [PACK-education → archived, merged into PACK-MIM]
        │
        ├──▶ PACK-verification (Pack: Верификация и приёмка — трансдоменный)
        │
        ├──▶ PACK-ecosystem (Pack: Экосистема — чёрный ящик)
        │     │
        │     ├──▶ DS-ecosystem-development (DS/governance)
        │     ├──▶ docs (DS/surface)
        │     ├──▶ DS-marathon-v2-tseren (DS/surface)
        │     └──▶ DS-principles-curriculum (DS/surface)
        │
        ├──▶ PACK-digital-platform (Pack: ИТ-платформа)
        │     │
        │     ├──▶ DS-twin (DS/instrument)
        │     ├──▶ digital-twin-mcp (DS/instrument)
        │     ├──▶ DS-my-strategy (DS/governance — агент Стратег)
        │     ├──▶ DS-ai-systems (DS/instrument — 7 ИИ-систем)
        │     ├──▶ activity-hub (DS/instrument — единая точка записи событий)
        │     ├──▶ knowledge-mcp (DS/instrument — поиск по знаниям)
        │     ├──▶ guides-mcp (DS/instrument — руководства)
        │     └──▶ fsm-mcp (DS/instrument — конечные автоматы)
        │
        └──▶ FMT-S2R (Base/Форматы)
              │
              └──▶ DS-ecosystem-development (DS/governance)

FMT-exocortex-template (Base/Форматы, setup.sh встроен)
  │
  └──▶ DS-ai-systems/setup (DS/instrument, author-side: template-sync)
```

---

## Обязательный контракт

Каждый репозиторий экосистемы **ДОЛЖЕН** иметь:

### 1. Признак типа в README.md (первая строка после заголовка)

```markdown
> **Тип репозитория:** `Base/Принципы` | `Base/Форматы` | `Pack` | `DS/instrument` | `DS/governance` | `DS/surface` | `PD` | `MC`
```

### 2. Файл `REPO-TYPE.md` (только свои репо)

`REPO-TYPE.md` размещается только в репозиториях, которые создал пользователь (в т.ч. на аккаунте организации aisystant).
Для чужих репо (ailev/FPF, aisystant/aisystant, aisystant/SystemsSchool_bot и др.) описание хранится только в этом реестре — не в самом репо.

---

## Правила

1. **Pack — единственный source-of-truth**. DS меняется вслед за Pack
2. **Один репозиторий — один тип**. Не смешивать Pack и DS
3. **При изменении Pack** — обновить DS
4. **При добавлении репозитория** — обновить этот реестр
5. **При удалении репозитория** — обновить этот реестр
6. **REPO-TYPE.md** — только в своих репозиториях (созданных пользователем, в т.ч. на org-аккаунте). Для чужих — описание только в этом реестре

---

*Последнее обновление: 2026-09-03* (РП-526, пир-сессия с Кодексом `2026-09-03-16-wp526-dashboard-clone-closure`: полная сверка всех 51 репозитория аккаунта TserenTserenov — добавлены 18 отсутствовавших записей #44-61, исправлено устаревшее имя `personal-guide`→`DS-personal-guide`, найдены и вынесены отдельно 8 неклассифицированных/сомнительных репозиториев)
