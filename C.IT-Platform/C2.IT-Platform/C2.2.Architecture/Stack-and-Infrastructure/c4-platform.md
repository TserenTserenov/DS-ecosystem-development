---
status: active
wp: WP-158
phase: "Ф4 (актуализация + view-диаграммы)"
created: 2026-04-01
updated: 2026-04-03
related: [WP-73, WP-159, WP-187, WP-200, DP.ARCH.001]
---

# C4-диаграммы платформы Aisystant

> **Source-of-truth архитектуры:** [DP.ARCH.001](../../PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ARCH.001-platform-architecture.md)
> **Deployment as-is:** [deployment.md](deployment.md)
> **ADR:** [ADR-IWE-001](../../Data-Stores/ADR-IWE-001-embeddings-isolation.md), [ADR-IWE-003](../../System-Implementations/ADR-IWE-003-gateway-backend-interface.md), [ADR-IWE-004](../../System-Implementations/ADR-IWE-004-github-app-installation-token.md)

---

<details open>
<summary><b>C4 L1 -- Системный контекст</b></summary>

Показывает: кто использует платформу и с какими внешними системами она взаимодействует.

```mermaid
C4Context
    title Aisystant Platform -- System Context (C4 L1)

    Person(user_learner, "Участник", "T1-T5. Обучается, развивает экзокортекс. AI через Gateway или бот.")
    Person(user_iwe, "Созидатель (IWE)", "T3-T5. Claude Code + MCP / Gateway.")
    Person(user_admin, "Администратор", "Управляет платформой, контентом, подписками.")

    System(platform, "Aisystant Platform", "ИТ-платформа развития интеллекта. 3-слойная: Интерфейсы - Обработка - Данные. Ory авторизация.")

    System_Ext(telegram, "Telegram", "Мессенджер. Точка входа через бота.")
    System_Ext(lms, "Aisystant LMS", "Профили, подписки, контент курсов.")
    System_Ext(anthropic, "LLM-провайдеры", "Anthropic Claude, OpenAI GPT. Backend для агентов и LLM Proxy.")
    System_Ext(github, "GitHub", "Pack-репо пользователей. GitHub App для write (ADR-IWE-004). CI/CD.")
    System_Ext(payments, "Платежные системы", "Stripe, YooKassa. Подписки и разовые платежи.")
    System_Ext(ext_oauth, "OAuth-интеграции", "Google Calendar, WakaTime, Linear.")
    System_Ext(ai_client, "AI-клиент", "Claude Code, ChatGPT, Gemini, Cursor. Подключается к Gateway как MCP.")

    Rel(user_learner, platform, "Обучается, AI через Gateway", "Telegram / MCP / Web")
    Rel(user_iwe, platform, "Работает с экзокортексом", "Claude Code + MCP")
    Rel(user_admin, platform, "Управляет", "Web / API")

    Rel(platform, telegram, "Webhook + Bot API", "HTTPS")
    Rel(platform, lms, "Профили, подписки", "REST API")
    Rel(platform, anthropic, "LLM-запросы через LLM Proxy", "REST API")
    Rel(platform, github, "Pack-репо, GitHub App tokens", "REST API")
    Rel(platform, payments, "Подписки, платежи", "REST API")
    Rel(platform, ext_oauth, "Интеграции пользователя", "OAuth2")

    Rel(ai_client, platform, "MCP-инструменты через Gateway", "MCP / HTTPS")
```

**Изменения 3 апреля vs 1 апреля:**
- Ory перенесён внутрь платформы (self-hosted, не external)
- Добавлены платежные системы (Stripe/YooKassa)
- LLM-провайдеры обобщены (Anthropic + OpenAI, через LLM Proxy)
- Участник тоже имеет доступ к AI через Gateway (не только Созидатель)

</details>

---

<details open>
<summary><b>C4 L2 -- Overview (карта контейнеров)</b></summary>

Все контейнеры платформы, сгруппированные по слоям. Без потоков данных (потоки -- в view-диаграммах ниже).

```mermaid
C4Container
    title Aisystant Platform -- Container Overview (C4 L2)

    System_Boundary(layer3, "Слой 3: Интерфейсы") {
        Container(aist_bot, "Aist Bot", "Python, Railway", "Telegram-интерфейс. Webhook. Тонкий клиент.")
        Container(lms_web, "LMS Web", "Aisystant", "Веб-интерфейс обучения.")
        Container(knowledge_gw, "Knowledge Gateway", "CF Worker", "Единый MCP endpoint. Ory-авт. Fan-out L2+L4+DT. (WP-187)")
    }

    System_Boundary(layer2a, "Слой 2А: ИИ-агенты (stateless, LLM)") {
        Container(agent_guide, "Проводник", "Claude API", "Онбординг, навигация, ответы.")
        Container(agent_strategist, "Стратег", "Claude API", "Планирование, дневные/недельные планы.")
        Container(agent_ke, "Знание-Экстрактор", "Claude API", "Извлечение знаний из сессий в Pack.")
        Container(agent_checker, "ДЗ-Чекер", "Claude API", "Проверка домашних заданий.")
    }

    System_Boundary(layer2b, "Слой 2Б: Детерминированные сервисы (stateful)") {
        Container(knowledge_mcp, "Knowledge MCP", "CF Worker, pgvector", "Семантический поиск по Pack (L2 Platform).")
        Container(guides_mcp, "Guides MCP", "CF Worker", "Гайды и руководства.")
        Container(dt_mcp, "Digital Twin MCP", "CF Worker, KV", "Цифровой двойник пользователя.")
        Container(personal_mcp, "Personal Knowledge MCP", "CF Worker", "L4: индекс личного Pack. Write через GitHub App (ADR-IWE-004).")
        Container(llm_proxy, "LLM Proxy", "CF Worker / Railway", "Роутинг по моделям, учет токенов per user_id, лимиты по тарифу. (WP-200)")
        Container(ory_svc, "Ory Stack", "Self-hosted", "Kratos (auth) + Hydra (OAuth2). Identity, SSO, токены.")
        Container(crm_billing, "CRM + Billing", "Directus + adapters", "CRM (WP-183), Stripe/YooKassa, Metabase дашборды.")
    }

    System_Boundary(layer1, "Слой 1: Данные") {
        ContainerDb(neon_db, "Neon PostgreSQL", "PostgreSQL + pgvector", "Платформенная БД. RLS per user_id (ADR-IWE-001).")
        ContainerDb(cf_kv, "Cloudflare KV", "KV Store", "Кэш Digital Twin.")
        ContainerDb(github_repos, "GitHub Repos", "Git", "Pack-репо (платформенные + пользовательские BYOB).")
    }
```

### Маппинг контейнеров - слои DP.ARCH.001

| Слой | Зона | Контейнеры | Характер |
|------|------|-----------|---------|
| 3. Интерфейсы | -- | Aist Bot, LMS Web, **Knowledge Gateway** | Тонкие клиенты, без бизнес-логики |
| 2. Обработка | А: ИИ-системы | Проводник, Стратег, KE, ДЗ-Чекер | Stateless, LLM, высокая стоимость |
| 2. Обработка | Б: Детерминированные | Knowledge MCP, Guides MCP, DT MCP, **Personal Knowledge MCP**, **LLM Proxy**, Ory Stack, **CRM + Billing** | Stateful, точное тестирование |
| 1. Данные | -- | Neon PostgreSQL, Cloudflare KV, GitHub Repos | Персистентность |

**Изменения 3 апреля vs 1 апреля:**
- Knowledge Gateway: `⏳ будущее` -> **active** (WP-187 done, E2E verified)
- Personal Knowledge MCP: `⏳ будущее` -> **active** (write через GitHub App, ADR-IWE-004)
- **+LLM Proxy** (WP-200): роутинг, учет токенов, Ory-авт.
- **+CRM + Billing** (WP-183 Phase 3): Directus, Stripe/YooKassa
- Ory: "cloud" -> **self-hosted** (Kratos + Hydra)
- FSM MCP удален (FSM внутри бота, не отдельный сервис)
- Gateway перенесен в Слой 3 (интерфейс, точка входа для AI-клиентов)

</details>

---

<details>
<summary><b>C4 L2-a -- Interface View (как пользователь входит)</b></summary>

```mermaid
C4Container
    title L2-a: Interface View -- точки входа пользователей

    Person(user_learner, "Участник", "T1-T5")
    Person(user_iwe, "Созидатель (IWE)", "T3-T5")

    System_Ext(telegram, "Telegram API", "api.telegram.org")
    System_Ext(ai_client, "AI-клиент", "Claude Code, ChatGPT, Cursor")
    System_Ext(lms, "Aisystant LMS", "system-school.ru")

    System_Boundary(interfaces, "Слой 3: Интерфейсы") {
        Container(aist_bot, "Aist Bot", "Python, Railway", "Telegram-интерфейс. Webhook.")
        Container(lms_web, "LMS Web", "Aisystant", "Веб-интерфейс обучения.")
        Container(knowledge_gw, "Knowledge Gateway", "CF Worker", "Единый MCP endpoint. Ory-авт. Fan-out по backend MCP.")
    }

    Container(ory_svc, "Ory Stack", "Self-hosted", "Kratos + Hydra. Identity, SSO.")

    %% Участник
    Rel(user_learner, aist_bot, "Сообщения", "Telegram")
    Rel(user_learner, lms_web, "Курсы, ДЗ", "HTTPS")
    Rel(user_learner, knowledge_gw, "AI через подписку", "MCP / HTTPS")

    %% Созидатель
    Rel(user_iwe, knowledge_gw, "MCP-инструменты", "MCP / HTTPS")

    %% AI-клиент
    Rel(ai_client, knowledge_gw, "MCP connector URL", "MCP / HTTPS")

    %% Telegram -> бот
    Rel(telegram, aist_bot, "Webhook POST", "HTTPS")

    %% Авторизация
    Rel(knowledge_gw, ory_svc, "OAuth2 токен", "OIDC")
    Rel(aist_bot, ory_svc, "Проверка подписки", "OAuth2")
    Rel(aist_bot, lms, "Профиль пользователя", "REST API")
```

**Ключевое:** Gateway -- единая точка входа для всех AI-клиентов. Бот -- для Telegram. LMS Web -- legacy-интерфейс.

</details>

---

<details>
<summary><b>C4 L2-b -- Processing View (как обрабатывается запрос)</b></summary>

```mermaid
C4Container
    title L2-b: Processing View -- обработка запросов

    Container(aist_bot, "Aist Bot", "Python", "S-1: агенты пока внутри бота (coupling)")
    Container(knowledge_gw, "Knowledge Gateway", "CF Worker", "Fan-out по backend MCP")

    System_Boundary(agents, "Слой 2А: ИИ-агенты (stateless)") {
        Container(agent_guide, "Проводник", "Claude API", "Онбординг, навигация")
        Container(agent_strategist, "Стратег", "Claude API", "Планирование")
        Container(agent_ke, "Знание-Экстрактор", "Claude API", "KE из сессий в Pack")
        Container(agent_checker, "ДЗ-Чекер", "Claude API", "Проверка ДЗ")
    }

    System_Boundary(services, "Слой 2Б: Детерминированные сервисы") {
        Container(knowledge_mcp, "Knowledge MCP", "CF Worker", "L2 Platform: семантический поиск")
        Container(guides_mcp, "Guides MCP", "CF Worker", "Руководства")
        Container(dt_mcp, "Digital Twin MCP", "CF Worker", "Профиль, прогресс")
        Container(personal_mcp, "Personal Knowledge MCP", "CF Worker", "L4: личный Pack пользователя")
        Container(llm_proxy, "LLM Proxy", "CF Worker", "Роутинг по моделям, учет токенов")
    }

    System_Ext(anthropic, "LLM-провайдеры", "Anthropic, OpenAI")

    %% Бот -> агенты (S-1: coupling, пока в одном сервисе)
    Rel(aist_bot, agent_guide, "Делегирует диалог", "internal")
    Rel(aist_bot, agent_strategist, "Делегирует планирование", "internal")
    Rel(aist_bot, agent_ke, "Делегирует KE", "internal")
    Rel(aist_bot, agent_checker, "Делегирует проверку", "internal")

    %% Gateway -> backend MCP (ADR-IWE-003: Backend Interface)
    Rel(knowledge_gw, knowledge_mcp, "L2 Platform", "MCP")
    Rel(knowledge_gw, dt_mcp, "Digital Twin", "MCP")
    Rel(knowledge_gw, personal_mcp, "L4 Personal", "MCP")

    %% Агенты -> MCP
    Rel(agent_guide, knowledge_mcp, "Поиск контекста", "MCP")
    Rel(agent_guide, dt_mcp, "Данные пользователя", "MCP")
    Rel(agent_strategist, dt_mcp, "Прогресс", "MCP")
    Rel(agent_strategist, knowledge_mcp, "Релевантный контент", "MCP")
    Rel(agent_ke, guides_mcp, "Шаблоны KE", "MCP")
    Rel(agent_checker, knowledge_mcp, "Критерии оценки", "MCP")

    %% LLM Proxy -> провайдеры
    Rel(aist_bot, llm_proxy, "LLM-запросы", "REST API")
    Rel(llm_proxy, anthropic, "Проксирование", "REST API")
```

**Ключевое:**
- **S-1 (coupling):** агенты пока физически внутри бота. Путь к разделению -- серверные агенты через Gateway (WP-201)
- **LLM Proxy:** все LLM-вызовы через единую точку (не напрямую в Anthropic)
- **Gateway fan-out:** ADR-IWE-003 формализует контракт backend MCP (initialize, tools/list, tools/call, search)

</details>

---

<details>
<summary><b>C4 L2-c -- Data View (где хранятся данные)</b></summary>

```mermaid
C4Container
    title L2-c: Data View -- хранение и изоляция данных

    System_Boundary(services, "Слой 2Б: Сервисы") {
        Container(knowledge_mcp, "Knowledge MCP", "CF Worker", "L2 Platform: pgvector search")
        Container(dt_mcp, "Digital Twin MCP", "CF Worker", "Профиль, характеристики")
        Container(personal_mcp, "Personal Knowledge MCP", "CF Worker", "L4: индекс личного Pack")
        Container(crm_billing, "CRM + Billing", "Directus", "CRM, подписки, платежи")
    }

    System_Boundary(data, "Слой 1: Данные") {
        ContainerDb(neon_db, "Neon PostgreSQL", "pgvector + RLS", "Платформенная БД. Эмбеддинги, ЦД, подписки. RLS per user_id (ADR-IWE-001).")
        ContainerDb(cf_kv, "Cloudflare KV", "KV Store", "Кэш Digital Twin (DIGITAL_TWIN_DATA).")
        ContainerDb(github_repos, "GitHub Repos", "Git", "Pack-репо. BYOB: данные у пользователя.")
    }

    System_Ext(github_api, "GitHub API", "api.github.com")
    System_Ext(payments, "Stripe / YooKassa", "Платежные провайдеры")

    %% MCP -> Neon
    Rel(knowledge_mcp, neon_db, "Эмбеддинги L2, поиск", "PostgreSQL + pgvector")
    Rel(dt_mcp, neon_db, "Профиль, события", "PostgreSQL")
    Rel(dt_mcp, cf_kv, "Кэш двойника", "KV API")
    Rel(personal_mcp, neon_db, "Эмбеддинги L4, namespace per user_id", "PostgreSQL + pgvector")
    Rel(crm_billing, neon_db, "Подписки, транзакции", "PostgreSQL")

    %% Personal MCP -> GitHub (write)
    Rel(personal_mcp, github_api, "Write через GitHub App Installation Token (1h TTL, ADR-IWE-004)", "REST API")
    Rel(github_repos, github_api, "Push/Pull Pack-репо", "Git")

    %% Billing -> платежи
    Rel(crm_billing, payments, "Подписки, webhook", "REST API")
```

**Ключевое:**
- **ADR-IWE-001:** multi-tenant изоляция эмбеддингов через namespace per user_id в pgvector (до 30k пользователей, затем Qdrant)
- **ADR-IWE-004:** запись в Pack пользователя через GitHub App Installation Token (1h TTL, минимальный scope contents:write)
- **BYOB:** данные пользователя в его GitHub-репо, эмбеддинги на платформе (Neon с RLS)

</details>

---

<details>
<summary><b>Сигналы для WP-73</b></summary>

> Полный маппинг C4 L2 -> deployment nodes: [deployment.md](deployment.md)

| ID | Компонент | Описание | Тип | Статус |
|----|-----------|---------|-----|--------|
| **S-1** | Aist Bot | ИИ-агенты (Слой 2А) и Telegram-интерфейс (Слой 3) в одном сервисе. Нельзя масштабировать независимо. | Coupling 2А+3 | Открыт. Путь: серверные агенты через Gateway (WP-201) |
| **S-2** | Aist Bot -> Neon | Бот напрямую пишет в Neon, минуя MCP. Интерфейс не должен знать о хранении. | Bypass слоя 2Б | Открыт |
| ~~**S-3**~~ | ~~AI-клиент -> MCP~~ | ~~Нет единой точки авторизации~~ | ~~Отсутствие Gateway~~ | **Resolved 3 апр:** Knowledge Gateway live (WP-187) |
| **S-4** | Langfuse | Observability только localhost, нет трейсинга в prod. | Наблюдаемость | Открыт |
| **S-5** | LLM-вызовы | Каждый агент/бот держит свой API-ключ Anthropic. Нет единого учета токенов, роутинга, лимитов. | Отсутствие LLM Proxy | Открыт. Путь: WP-200 |

</details>

---

<details>
<summary><b>История</b></summary>

| Дата | Фаза | Изменение |
|------|------|---------|
| 2026-04-01 | Ф0 | Концепция, акторы L1, контейнеры L2 по 3 слоям, ключевой инвариант IWE |
| 2026-04-01 | Ф1 | C4 L1 System Context в Mermaid |
| 2026-04-01 | Ф2 | C4 L2 Containers в Mermaid |
| 2026-04-01 | Ф3 | Ревью: сигналы S-1..S-4, перекрестные ссылки с deployment.md |
| 2026-04-03 | Ф4 | Актуализация по ADR-IWE-001/003/004, WP-187 done, WP-200/183. View-диаграммы (L2-a/b/c). S-3 resolved, S-5 новый |

</details>
