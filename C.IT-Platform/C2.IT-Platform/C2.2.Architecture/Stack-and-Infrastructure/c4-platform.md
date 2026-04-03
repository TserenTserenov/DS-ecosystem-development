---
status: active
wp: WP-158
phase: "Ф4 (view-диаграммы)"
created: 2026-04-01
updated: 2026-04-03
related: [WP-73, WP-159, WP-187, WP-200, DP.ARCH.001]
---

# C4-диаграммы платформы Aisystant

> **Source-of-truth архитектуры:** [DP.ARCH.001](../../PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.001-platform-architecture.md)
> **Deployment:** [deployment.md](deployment.md)
> **ADR:** [ADR-IWE-001](../../Data-Stores/ADR-IWE-001-embeddings-isolation.md), [ADR-IWE-003](../../System-Implementations/ADR-IWE-003-gateway-backend-interface.md), [ADR-IWE-004](../../System-Implementations/ADR-IWE-004-github-app-installation-token.md)

---

<details open>
<summary><b>C4 L1 -- Системный контекст</b></summary>

Кто использует платформу и с какими внешними системами она взаимодействует.

```mermaid
flowchart TB
    subgraph users ["Пользователи"]
        learner["Участник\nT1-T5"]
        creator["Созидатель IWE\nT3-T5"]
        admin["Администратор"]
    end

    platform["Aisystant Platform\n3-слойная архитектура\nОры-авторизация"]

    subgraph external ["Внешние системы"]
        telegram["Telegram"]
        lms["Aisystant LMS"]
        llm_providers["LLM-провайдеры\nAnthropic, OpenAI"]
        github["GitHub"]
        payments["Stripe / YooKassa"]
        oauth_vendors["OAuth-интеграции\nCalendar, WakaTime, Linear"]
    end

    subgraph ai_clients ["AI-клиенты"]
        claude_code["Claude Code"]
        chatgpt["ChatGPT"]
        cursor["Cursor / IDE"]
    end

    learner -- "Telegram / Web / Gateway" --> platform
    creator -- "Claude Code + MCP" --> platform
    admin -- "Web / Directus" --> platform

    claude_code -- "MCP connector" --> platform
    chatgpt -- "MCP connector" --> platform
    cursor -- "MCP connector" --> platform

    platform -- "Webhook + Bot API" --> telegram
    platform -- "Профили, подписки" --> lms
    platform -- "LLM-запросы через\nLLM Proxy ⏳ WP-200" --> llm_providers
    platform -- "Pack-репо, GitHub App" --> github
    platform -- "Подписки, платежи" --> payments
    platform -- "OAuth2" --> oauth_vendors
```

</details>

---

<details open>
<summary><b>C4 L2 -- Overview (карта контейнеров по слоям)</b></summary>

Все контейнеры платформы. Потоки данных -- в view-диаграммах ниже.

```mermaid
flowchart TB
    subgraph layer3 ["Слой 3: Интерфейсы"]
        bot["Aist Bot\nPython, Railway"]
        gateway["Knowledge Gateway\nCF Worker, Ory-авт."]
        webapp["Web App\nVue SPA"]
        directus["Directus\nCRM UI, Railway"]
        metabase["Metabase\nBI-дашборды, Railway"]
    end

    subgraph layer2a ["Слой 2А: ИИ-агенты — stateless, LLM"]
        guide["Проводник"]
        strategist["Стратег"]
        ke["Знание-Экстрактор"]
        checker["ДЗ-Чекер"]
    end

    subgraph layer2b ["Слой 2Б: Детерминированные сервисы — stateful"]
        knowledge_mcp["Knowledge MCP\nCF Worker, pgvector"]
        guides_mcp["Guides MCP\nCF Worker"]
        dt_mcp["Digital Twin MCP\nCF Worker"]
        fsm_mcp["FSM MCP\nCF Worker\n⏳ задеплоен, не используется"]
        personal_mcp["Personal Knowledge MCP\nCF Worker"]
        llm_proxy["LLM Proxy\nроутинг, учет токенов\n⏳ planned WP-200"]
        ory["Ory Stack\nKratos + Hydra, self-hosted"]
        billing["Billing Module\nадаптеры Stripe/YooKassa"]
    end

    subgraph layer1 ["Слой 1: Данные"]
        neon["Neon PostgreSQL\npgvector + RLS"]
        kv["Cloudflare KV"]
        repos["GitHub Repos\nPack платформенные + BYOB"]
    end
```

| Слой | Зона | Контейнеры | Характер |
|------|------|-----------|---------|
| 3. Интерфейсы | -- | Aist Bot, Knowledge Gateway, Web App, Directus (CRM), Metabase (BI) | Тонкие клиенты, UI |
| 2. Обработка | А: ИИ-системы | Проводник, Стратег, KE, ДЗ-Чекер | Stateless, LLM |
| 2. Обработка | Б: Детерминированные | Knowledge MCP, Guides MCP, DT MCP, FSM MCP (⏳), Personal Knowledge MCP, LLM Proxy (⏳), Ory Stack, Billing Module | Stateful |
| 1. Данные | -- | Neon PostgreSQL, Cloudflare KV, GitHub Repos | Персистентность |

</details>

---

<details>
<summary><b>C4 L2-a -- Interface View</b></summary>

Как пользователь входит в платформу.

```mermaid
flowchart LR
    learner["Участник\nT1-T5"]
    creator["Созидатель\nT3-T5"]
    admin["Администратор\nГиляна, Алёна, Юля"]
    ai_client["AI-клиент\nClaude Code\nChatGPT\nCursor"]

    subgraph interfaces ["Слой 3: Интерфейсы"]
        bot["Aist Bot\nTelegram-интерфейс"]
        gateway["Knowledge Gateway\nЕдиный MCP endpoint\nОры-авт., fan-out,\nBackend Registry,\nKnowledge Gate"]
        webapp["Web App\nVue SPA\nМой ЦД, подписки"]
        directus["Directus\nCRM: контакты, группы,\nоплаты, RBAC"]
        metabase["Metabase\nMRR, LTV, воронка,\nнаполняемость"]
    end

    ory["Ory Stack\nKratos + Hydra"]
    lms["Aisystant LMS"]
    telegram["Telegram API"]

    learner -- "Telegram" --> bot
    learner -- "AI через подписку" --> gateway
    learner -- "Веб" --> webapp
    creator -- "MCP-инструменты" --> gateway
    admin -- "CRM" --> directus
    admin -- "Аналитика" --> metabase
    ai_client -- "MCP connector URL" --> gateway

    telegram -- "Webhook" --> bot
    bot -- "Профиль" --> lms
    bot -- "Проверка подписки" --> ory
    gateway -- "OAuth2 токен" --> ory
    webapp -- "SSO" --> ory
    directus -- "SSO" --> ory
```

**Gateway** -- единая точка входа для AI-клиентов. Backend Registry + Knowledge Gate (ADR-IWE-003) обеспечивают динамическое подключение и валидацию BYOB MCP.
**Web App** -- SPA для управления ЦД, подписками, настройками.
**Directus** -- CRM для команды: контакты, группы, оплаты, RBAC (WP-183).
**Metabase** -- BI-дашборды: MRR, LTV, churn, воронка T0-T4, наполняемость (WP-183).
**Бот** -- Telegram-интерфейс, тонкий клиент.

</details>

---

<details>
<summary><b>C4 L2-b -- Processing View</b></summary>

Как обрабатывается запрос.

```mermaid
flowchart TB
    subgraph entry ["Точки входа"]
        bot["Aist Bot"]
        gateway["Knowledge Gateway\nBackend Registry\nKnowledge Gate"]
    end

    subgraph agents ["Слой 2А: ИИ-агенты"]
        guide["Проводник"]
        strategist["Стратег"]
        ke["Знание-Экстрактор"]
        checker["ДЗ-Чекер"]
    end

    subgraph mcp ["Слой 2Б: MCP-сервисы"]
        knowledge["Knowledge MCP\nL2 Platform"]
        guides["Guides MCP"]
        dt["Digital Twin MCP"]
        fsm["FSM MCP ⏳\nзадеплоен, не используется"]
        personal["Personal Knowledge MCP\nL4 Personal"]
    end

    subgraph billing_group ["Слой 2Б: Billing"]
        billing["Billing Module\nадаптеры Stripe/YooKassa"]
        directus["Directus\nCRM Flows"]
    end

    subgraph llm_group ["Слой 2Б: LLM ⏳"]
        llm_proxy["LLM Proxy ⏳ WP-200\nроутинг по моделям\nучет токенов per user_id\nлимиты по тарифу"]
    end

    llm_providers["LLM-провайдеры\nAnthropic, OpenAI"]

    bot -- "делегирует" --> guide
    bot -- "делегирует" --> strategist
    bot -- "делегирует" --> ke
    bot -- "делегирует" --> checker
    bot -. "⏳ планируется вынос FSM" .-> fsm

    gateway -- "L2 Platform" --> knowledge
    gateway -- "Digital Twin" --> dt
    gateway -- "L4 Personal" --> personal
    gateway -. "⏳ серверные агенты WP-201" .-> guide
    gateway -. "⏳ серверные агенты WP-201" .-> strategist

    guide -- "поиск контекста" --> knowledge
    guide -- "данные пользователя" --> dt
    strategist -- "прогресс" --> dt
    strategist -- "контент" --> knowledge
    ke -- "шаблоны" --> guides
    checker -- "критерии" --> knowledge

    bot -- "LLM-запросы (сейчас напрямую)" --> llm_providers
    bot -. "⏳ через LLM Proxy" .-> llm_proxy
    gateway -. "⏳ LLM для пользователей\nбез своего API-ключа" .-> llm_proxy
    llm_proxy -. "⏳ роутинг" .-> llm_providers

    directus -- "webhook: статус изменён" --> bot
    billing -- "событие оплаты" --> bot
```

**Текущее состояние (сплошные линии):**
- Бот вызывает LLM-провайдеров напрямую (каждый агент со своим API-ключом)
- Gateway fan-out по MCP-сервисам (knowledge, DT, personal)

**Планируемое (⏳ пунктир):**
- **LLM Proxy (WP-200):** единая точка LLM-вызовов. Пользователю не нужен свой API-ключ -- платформа оплачивает и включает в подписку. Роутинг по моделям, учёт токенов per user_id, лимиты по тарифу (trial / БР / превышение)
- **Серверные агенты (WP-201):** Gateway запускает агентов (Стратег, Экстрактор) от имени пользователя -- паритет T4 без CLI
- **FSM MCP:** вынос state machine из бота в отдельный сервис

**Архитектура Gateway:** Backend Registry (ADR-IWE-003 §6) -- динамическое подключение BYOB MCP. Knowledge Gate (§5, KG-01..KG-07) -- валидация нового backend.
**Directus Flows:** webhook-триггеры при смене статуса контакта -> бот добавляет/удаляет из чата (WP-183)

</details>

---

<details>
<summary><b>C4 L2-c -- Data View</b></summary>

Где хранятся данные и как обеспечена изоляция.

```mermaid
flowchart TB
    subgraph services ["Слой 2Б: Сервисы"]
        knowledge["Knowledge MCP"]
        dt["Digital Twin MCP"]
        personal["Personal Knowledge MCP"]
        billing["Billing Module"]
        directus["Directus"]
        metabase["Metabase"]
        llm_proxy["LLM Proxy ⏳"]
    end

    subgraph data ["Слой 1: Данные"]
        neon["Neon PostgreSQL\npgvector + RLS per user_id"]
        kv["Cloudflare KV\nкэш Digital Twin"]
        repos["GitHub Repos\nPack платформенные + BYOB"]
        metabase_db["Metabase App DB\nRailway Postgres"]
    end

    github_api["GitHub API"]
    payments["Stripe / YooKassa"]

    knowledge -- "эмбеддинги L2, поиск" --> neon
    dt -- "профиль, события" --> neon
    dt -- "кэш двойника" --> kv
    personal -- "эмбеддинги L4\nnamespace per user_id" --> neon
    billing -- "подписки, транзакции" --> neon
    directus -- "CRM: контакты, группы" --> neon
    metabase -- "read-only: аналитика" --> neon
    metabase -- "app data" --> metabase_db

    personal -- "write через GitHub App\nInstallation Token 1h TTL" --> github_api
    github_api --> repos

    llm_proxy -. "⏳ учёт токенов per user_id" .-> neon
    billing -- "подписки, webhook" --> payments
```

- **ADR-IWE-001:** multi-tenant изоляция эмбеддингов -- namespace per user_id в pgvector (до 30k, затем Qdrant)
- **ADR-IWE-004:** запись в Pack пользователя через GitHub App Installation Token (минимальный scope contents:write)
- **BYOB:** данные пользователя в его GitHub-репо, эмбеддинги на платформе (Neon с RLS)
- **Metabase:** отдельная App DB на Railway Postgres, read-only доступ к Neon для дашбордов (WP-183)

</details>

---

<details>
<summary><b>Сигналы для WP-73</b></summary>

> Полный маппинг C4 L2 -> deployment: [deployment.md](deployment.md)

| ID | Компонент | Описание | Тип | Статус |
|----|-----------|---------|-----|--------|
| **S-1** | Aist Bot | ИИ-агенты (2А) и Telegram-интерфейс (3) в одном сервисе | Coupling 2А+3 | Открыт. Путь: WP-201 |
| **S-2** | Aist Bot -> Neon | Бот напрямую пишет в Neon, минуя MCP | Bypass слоя 2Б | Открыт |
| ~~**S-3**~~ | ~~AI-клиент -> MCP~~ | ~~Нет единой точки авторизации~~ | ~~Нет Gateway~~ | Resolved: WP-187 |
| **S-4** | Langfuse | Observability только localhost, нет трейсинга в prod | Наблюдаемость | Открыт |
| **S-5** | LLM-вызовы | Каждый агент держит свой API-ключ. Нет учета токенов, роутинга | Нет LLM Proxy | Открыт. Путь: WP-200 |
| **S-6** | FSM внутри бота | FSM (core/machine.py) внутри бота, не вынесен в FSM MCP. Усиливает S-1 coupling | FSM coupling | Открыт. FSM MCP задеплоен, но не подключен |

</details>

---

<details>
<summary><b>История</b></summary>

| Дата | Фаза | Изменение |
|------|------|---------|
| 2026-04-01 | Ф0-Ф3 | C4 L1 + L2 в Mermaid, ревью, сигналы S-1..S-4 |
| 2026-04-03 | Ф4 | View-диаграммы (overview + Interface/Processing/Data). Flowchart для читаемости. Верификация по inbox |

</details>
