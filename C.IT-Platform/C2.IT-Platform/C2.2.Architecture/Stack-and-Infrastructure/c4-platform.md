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
    admin -- "Web / API" --> platform

    claude_code -- "MCP connector" --> platform
    chatgpt -- "MCP connector" --> platform
    cursor -- "MCP connector" --> platform

    platform -- "Webhook + Bot API" --> telegram
    platform -- "Профили, подписки" --> lms
    platform -- "LLM-запросы через Proxy" --> llm_providers
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
        personal_mcp["Personal Knowledge MCP\nCF Worker"]
        llm_proxy["LLM Proxy\nроутинг, учет токенов"]
        ory["Ory Stack\nKratos + Hydra, self-hosted"]
        crm["CRM + Billing\nDirectus, Stripe/YooKassa"]
    end

    subgraph layer1 ["Слой 1: Данные"]
        neon["Neon PostgreSQL\npgvector + RLS"]
        kv["Cloudflare KV"]
        repos["GitHub Repos\nPack платформенные + BYOB"]
    end
```

| Слой | Зона | Контейнеры | Характер |
|------|------|-----------|---------|
| 3. Интерфейсы | -- | Aist Bot, Knowledge Gateway, Web App | Тонкие клиенты, без бизнес-логики |
| 2. Обработка | А: ИИ-системы | Проводник, Стратег, KE, ДЗ-Чекер | Stateless, LLM |
| 2. Обработка | Б: Детерминированные | Knowledge MCP, Guides MCP, DT MCP, Personal Knowledge MCP, LLM Proxy, Ory Stack, CRM + Billing | Stateful |
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
    ai_client["AI-клиент\nClaude Code\nChatGPT\nCursor"]

    subgraph interfaces ["Слой 3: Интерфейсы"]
        bot["Aist Bot\nTelegram-интерфейс"]
        gateway["Knowledge Gateway\nЕдиный MCP endpoint\nОры-авторизация"]
        webapp["Web App\nVue SPA\nМой ЦД, подписки"]
    end

    ory["Ory Stack\nKratos + Hydra"]
    lms["Aisystant LMS"]
    telegram["Telegram API"]

    learner -- "Telegram" --> bot
    learner -- "AI через подписку" --> gateway
    learner -- "Веб" --> webapp
    creator -- "MCP-инструменты" --> gateway
    ai_client -- "MCP connector URL" --> gateway

    telegram -- "Webhook" --> bot
    bot -- "Профиль" --> lms
    bot -- "Проверка подписки" --> ory
    gateway -- "OAuth2 токен" --> ory
    webapp -- "SSO" --> ory
```

**Gateway** -- единая точка входа для всех AI-клиентов (один URL, Ory-авторизация, fan-out по backend MCP).
**Web App** -- SPA для управления ЦД, подписками, настройками (не AI-интерфейс).
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
        gateway["Knowledge Gateway"]
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
        personal["Personal Knowledge MCP\nL4 Personal"]
    end

    llm_proxy["LLM Proxy\nроутинг, учет токенов"]
    llm_providers["LLM-провайдеры\nAnthropic, OpenAI"]

    bot -- "делегирует" --> guide
    bot -- "делегирует" --> strategist
    bot -- "делегирует" --> ke
    bot -- "делегирует" --> checker

    gateway -- "L2 Platform" --> knowledge
    gateway -- "Digital Twin" --> dt
    gateway -- "L4 Personal" --> personal

    guide -- "поиск контекста" --> knowledge
    guide -- "данные пользователя" --> dt
    strategist -- "прогресс" --> dt
    strategist -- "контент" --> knowledge
    ke -- "шаблоны" --> guides
    checker -- "критерии" --> knowledge

    bot -- "LLM-запросы" --> llm_proxy
    llm_proxy -- "проксирование" --> llm_providers
```

- **S-1 (coupling):** агенты пока внутри бота. Путь к разделению -- серверные агенты через Gateway (WP-201)
- **LLM Proxy:** все LLM-вызовы через единую точку (роутинг, лимиты по тарифу)
- **Gateway fan-out:** ADR-IWE-003 формализует контракт backend MCP

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
        crm["CRM + Billing"]
    end

    subgraph data ["Слой 1: Данные"]
        neon["Neon PostgreSQL\npgvector + RLS per user_id"]
        kv["Cloudflare KV\nкэш Digital Twin"]
        repos["GitHub Repos\nPack платформенные + BYOB"]
    end

    github_api["GitHub API"]
    payments["Stripe / YooKassa"]

    knowledge -- "эмбеддинги L2, поиск" --> neon
    dt -- "профиль, события" --> neon
    dt -- "кэш двойника" --> kv
    personal -- "эмбеддинги L4\nnamespace per user_id" --> neon
    crm -- "подписки, транзакции" --> neon

    personal -- "write через GitHub App\nInstallation Token 1h TTL" --> github_api
    github_api --> repos

    crm -- "подписки, webhook" --> payments
```

- **ADR-IWE-001:** multi-tenant изоляция эмбеддингов -- namespace per user_id в pgvector (до 30k, затем Qdrant)
- **ADR-IWE-004:** запись в Pack пользователя через GitHub App Installation Token (минимальный scope contents:write)
- **BYOB:** данные пользователя в его GitHub-репо, эмбеддинги на платформе (Neon с RLS)

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

</details>

---

<details>
<summary><b>История</b></summary>

| Дата | Фаза | Изменение |
|------|------|---------|
| 2026-04-01 | Ф0-Ф3 | C4 L1 + L2 в Mermaid, ревью, сигналы S-1..S-4 |
| 2026-04-03 | Ф4 | Актуализация по ADR-IWE-001/003/004. View-диаграммы (overview + Interface/Processing/Data). Flowchart вместо C4-нотации для читаемости |

</details>
