---
type: architect-agenda
title: "Встреча 4 с архитектором (7 апр) — открытые вопросы"
status: pending
created: 2026-04-01
updated: 2026-04-07
depends_on: WP-73, WP-187, WP-109, WP-183
source: встречи 1 (29 мар) + 2 (31 мар) + 3 (5 апр) + 4 (7 апр) — закрытые решения ниже и в архиве
---

# Повестка: встреча 4 (7 апреля 14:00–15:00)

> **Встречи 1-3** закрыли: Блок А+Б+В, Keto-модель, Gateway = прозрачный прокси, knowledge base разделение.
> **ADR:** ADR-IWE-003 (Gateway Backend Interface), ADR-IWE-004 (GitHub App Token), ADR-IWE-005 (ingest_event), ADR-IWE-007 (Content Integrity) — приняты.
> **W14 итог:** R2 Архитектура Phase 2 DONE, R9 Knowledge Gateway DONE (reopened SSE/L2/L4), R1 Ory верифицирована. Мультипликатор 2.68x.
> Здесь -- только то, что осталось открытым для обсуждения.

---

## 1. Ory Gateway -- ⏳ в работе у Паши (~5 мин)

**Статус (7 апр):** R1 Ory OAuth верифицирована (5 апр). `gateway-mcp` и `aist-bot` клиенты активны, Hydra под `/hydra/` prefix.

`auth.aisystant.com` — нужно подтвердить: 404 устранён или endpoint переехал?

**Нужно:**
- Актуальный URL Keto (задеплоен ли Keto? если да — URL для `POST /check`)
- Статус Натальи — разблокирована?
- Сроки переключения на сервер (→ #6)

**Контекст:** Ory Network в проде (`thirsty-goldstine-5xjpbvdi2b.projects.oryapis.com`), PKCE flow работает в digital-twin-mcp и gateway-mcp.

---

## 2. Проверка подписки через Keto -- ✅ решено (5 апр)

### Решение (оперативка 5 апр)

**Подтверждён вариант Б -- Ory Keto.** Модель:
- Атомарные **permissions** (напр. `enter_group_chat`, `post_comments`, `access_navigator`) объединяются в **роли** (напр. `subscribers`)
- Все участники роли `subscribers` получают набор permissions, назначенных этой роли
- Все подсистемы видят, что пользователь в группе `subscribers`, и реализуют доступ по-разному

**Стратегия внедрения:** начать с новых сервисов (семинары -- уже работает webhook с Димой, семинар IWE принимает оплату через бота). Потом постепенно переводить остальное на Keto.

**Фаза A (сейчас):** Webhook Payment Registry → бот уже работает. Бот читает Payment Registry напрямую для проверки.
**Фаза B:** Миграция на Keto. Billing Service при оплате записывает relation tuples в Keto. Бот проверяет через `POST /check`.

### Остаётся открытым

- **Ревью Q-keto карты permissions (6 апр):** 6 namespaces, ~45 атомарных permissions, 11 role-groups — Андрей валидирует? (см. §Q-keto ниже)
- **DE-34** (привязка `ory_id ↔ lms_user_id`) -- в Linear Backlog, блокирует Keto для существующих пользователей. Статус?
- **Фаза A (семинары):** готовность Паши к реализации Keto relation tuples?

---

## 3. Gateway = прозрачный прокси -- ✅ решено (5 апр)

### Решение (оперативка 5 апр)

**Gateway НЕ должен фильтровать, нормализовать или объединять результаты.** Позиция Андрея:

- Gateway = авторизация пользователя + определение доступных MCP + проброс ответов as-is
- Если Gateway начнёт фильтровать по score или преобразовывать -- это уже не gateway, а более сложная штука
- Каждый MCP -- это отдельный инструмент для LLM. LLM видит N инструментов и сама решает, что использовать
- Порог score, нормализация, ранжирование -- ответственность **клиента** (LLM / агентный фреймворк), не Gateway
- Если MCP выдаёт много мусора -- проблема в данных MCP (плохой ingestion), а не в Gateway

**Следствия:**
- Вопросы 3а (cutoff) и 3б (нормализация между моделями) **снимаются** с повестки Gateway
- ADR-IWE-003 §score-normalization: нормализация [0,1] остаётся обязательной для каждого бэкенда, но Gateway не пересчитывает и не сравнивает scores между бэкендами
- Рассмотреть Cloudflare AI Gateway как готовое решение (авторизация + проброс). Нужно проверить совместимость с нашими политиками

### Остаётся открытым

- **Cloudflare AI Gateway vs свой:** проверить, подходит ли CF AI Gateway для нашего use case (MCP проброс + Ory авторизация). Если нет -- свой, минимальный
- **Gateway v2.0 deployed (6 апр):** OAuth proxy + Streamable HTTP работают. Нужно ли что-то менять в контракте ADR-IWE-003?

---

## 4. Knowledge base: разделение контекстов -- ✅ принцип решён (5 апр)

### Решение (оперативка 5 апр)

Три уровня баз знаний: **личная, проектная, публичная.** Ключевые принципы:

- **Разные репозитории, один способ работы.** Личная база, проект с семьёй, рабочий проект, публичный контент -- это разные репозитории, но архитектурно одинаковые (те же MCP, тот же ingestion, тот же Gateway)
- **Gateway = окно в репозиторий.** Один Gateway, разные контексты. Пользователь видит свои MCP-инструменты в зависимости от подключённых репозиториев
- **Командная работа -- на уровне платформы.** Личный Gateway -- сейчас. Командный (общий репо для команды) -- позже, на платформе. Код будет один, вопрос подключения командных репозиториев
- **Community MCP (витрина публичных MCP)** -- отложен на потом. Каждый может выдать свои MCP для подключения другими. Обсудим позже

### Остаётся открытым

- **Как объединять контексты?** Личное стратегирование, разные команды, публичное -- как Gateway показывает нужный контекст? Переключение между репозиториями или единый поиск?
- **Миграция между контекстами.** Мысль из приватной базы (семья) → публичная база. Процедура переноса -- ручная или автоматическая?
- **Permission-модель для командных репозиториев.** Кто имеет доступ, как приглашать, как отзывать?

---

## 5. GDPR / Репликация RU↔EU -- ⏸️ отложено (5 апр)

### Статус (оперативка 5 апр)

Проблема зафиксирована, но **решение отложено.** Олег (юрист) предупредил о рисках:
- Если общая база со всеми пользователями -- европейцы спросят: «почему русские данные в нашей базе?»
- Копировать европейцев в Россию -- нарушение GDPR (локализация данных)
- Копировать русских в Европу -- рискованно (могут спросить, зачем русские идентификаторы в EU)

Андрей: «Надо думать. Google же работает в России с общими идентификаторами.» Варианты:
- Отказаться от репликации вообще
- Делать по запросу (при первом входе в другую юрисдикцию -- регистрация нового аккаунта с тем же email)
- Общие идентификаторы в Ory, но данные раздельно (признак юрисдикции в Ory)

### Что осталось от предыдущей повестки (для будущего обсуждения)

Принцип разделения не определён. Два подхода:

| Принцип | Суть |
|---------|------|
| По юрисдикции пользователя | Данные россиян в RU, остальных в EU. Один пользователь -- одна нода |
| По типу данных | PII в RU для россиян, контент в EU для всех |

Ключевой вопрос: Activity Hub и Digital Twin -- это PII?

**Следующий шаг:** юридическая консультация. Вернуться к вопросу после уточнения правовых рисков.

---

## 6. Новый сервер -- ⏳ после Ory (5 апр)

### Статус (оперативка 5 апр)

Андрей сейчас разблокирует Наталью по Ory, потом переключится на сервер. Конкретного плана пока нет.

### Кандидаты на переезд

| Сервис | Зачем на сервер | Приоритет |
|--------|----------------|-----------|
| Ory self-hosted (Kratos + Hydra + Keto) | 152-ФЗ: identity россиян в РФ (решение Б1, 29 мар) | Высокий -- блокирует RU-ноду |
| Neon RU-нода (или self-hosted PG) | 152-ФЗ: PII россиян | Зависит от решения по репликации (#5) |
| Activity Hub | Write-heavy, Railway дорогой | Средний |
| Gateway | Latency для РФ | Низкий -- CF Workers могут проксировать |

### Что нужно решить (на следующей встрече)

1. **Что первым?** Предположение: Ory self-hosted
2. **Сетевая связность:** сервер ↔ Railway ↔ Neon EU
3. **Что НЕ переезжает?** Бот на Railway? Knowledge-mcp на CF?

---

## 7. WP-187 — Knowledge Gateway: GitHub App + E2E -- ⏳ (~10 мин)

**Статус (7 апр):** Ф4.0 DONE (6 апр) — multi-user onboarding deployed. Gateway v2.0 с OAuth proxy + Streamable HTTP.

**Открытые вопросы для Андрея:**

| # | Вопрос | Контекст |
|---|--------|----------|
| 7a | **GitHub App Setup URL** | Сейчас ручной. Автоматизация через OAuth callback? Или достаточно документации? |
| 7b | **ADR-IWE-004 валидация** | GitHub App Installation Token (1h TTL) — Андрей подтверждает подход? Security concerns? |
| 7c | **E2E тест-план** | Какие сценарии покрыть? Минимум: onboarding → ingestion → search → результат |
| 7d | **Ф4.1-4.4 приоритезация** | delete-инструмент, управление ролями, Ф3.5 именование — что первым? |

---

## 8. WP-109 — Event Bus / Activity Hub -- ⏳ (~10 мин)

**Статус (7 апр):** ADR-IWE-005 accepted (5 апр). Разблокирован для реализации.

**Решение (ADR-IWE-005):** `personal-knowledge-mcp` при мутациях (write/propose_capture) делает direct INSERT `ingest_event` в Activity Hub. Gateway остаётся прозрачным прокси — не участвует в событиях.

**Открытые вопросы для Андрея:**

| # | Вопрос | Контекст |
|---|--------|----------|
| 8a | **Direct INSERT vs HTTP** | ADR-IWE-005 говорит direct DB. Андрей подтверждает? Или лучше HTTP endpoint в Activity Hub? |
| 8b | **Контракт события** | 5 типов (§3.10 секция E). Достаточно? Нужны ли дополнительные? |
| 8c | **WP-45 Ф4 зависимость** | WP-45 Ф4 blocked на WP-109. Приоритет Event Bus в W15? |

---

## Дополнительно: вопросы из WP-183 / unified-payments

> Контекст: WP-183-unified-payments-proposal обновлён 4 апреля. Принятые решения Р1-Р6 закрыли часть вопросов. Ниже -- то, что остаётся открытым для Андрея.

### Закрыто (4 апр, не обсуждаем)

| Решение | Суть |
|---------|------|
| Р1 | Payment Registry (SYS.011) -- единый источник правды по оплатам |
| Р2 | Две подсистемы: Payment Registry (учёт) + Billing Service (бизнес-логика). На Фазе B -- миграция в одну |
| Р3 | Webhook: Payment Registry → бот (один канал, один контракт) |
| Р5 | Допуск в чат: бот генерирует одноразовую ссылку (вариант А) |
| Р6 | Бот МИМ тоже принимает оплаты, оба регистрируют в Payment Registry |
| А1-А4 | RLS, Keto, Chargeback не нужен пока, Directus+Metabase подтверждён |

### Открыто для Андрея (архитектор)

| # | Вопрос | Суть | Контекст |
|---|--------|------|----------|
| Р4 | Привязка identity через Ory (Фаза B) | `tg_id ↔ email ↔ aisystant_id` -- звезда через Ory. Как Ory становится hub'ом identity? Где маппинг до Ory (Фаза A)? | Блокирует Фазу B. Связано с DE-34 |
| Б5 | Каналы для команд (SC-8) | TG-группы vs Discord vs Zulip для учебных команд. Не блокер (Team Service в Фазе 2), но нужно мнение архитектора | WP-73 §5.1 Q6, WP-74 SC-8 |
| ADR-IWE-007 | Content Integrity при индексации | Ревью proposed ADR: exclusion list (CLAUDE.md), manifest hash, content validation, staleness detection | WP-73 Phase 2, WP-187 |
| ~~Q-billing~~ | ~~Activity Hub billing adapter~~ | ~~✅ **Закрыт (6 апр).** Формат: §3.10 секция E (5 типов). Паттерн: ADR-IWE-005~~ | |
| ~~Q-keto~~ | ~~Keto: перечень permissions~~ | ~~🔶 **Проработан (6 апр) — см. §Q-keto ниже.** Ревью с командой → Паша (DevOps) реализует~~ | |

### Перенесено в WP-183 (Ильшат+Дима)

| # | Вопрос | Суть |
|---|--------|------|
| Q-points | Баллы — placeholder `point_ledger` в Фазе A? | unified-payments §0.1, Фаза C |
| Q-consolidation | Два хранилища оплат: всё в Neon или два + Directus? | unified-payments §0.1 |
| Q-monolith | Декомпозиция монолита: Payment Registry первый, потом CRM | Решение 5 апр |

---

## Q-keto: Карта атомарных permissions (проработка 6 апр)

> **Модель (ADR-014):** `Permission = Entitlement ∩ Role ∩ Scope`. Три оси:
> - **Entitlement** (тир): что ДОСТУПНО по подписке (T1-T4, TM1-TM3, TA1-TA4, TD1)
> - **Role**: что можно ДЕЛАТЬ (learner, mentor, admin, developer)
> - **Scope**: над ЧЕМ (cohort:X, program:Y, user:Z, global)
>
> **Реализация:** Ory Keto (Zanzibar ReBAC). Атомарные permissions объединяются в role-groups.
> **Стратегия внедрения (5 апр):** начать с новых сервисов (семинары), потом переводить остальное.

### Пространства имён (namespaces)

| Namespace | Описание | Примеры объектов |
|-----------|----------|-----------------|
| `platform` | Платформенные функции | `knowledge`, `guides`, `digital_twin`, `gateway` |
| `ai` | ИИ-системы (роли R1-R28) | `consultant`, `navigator`, `strategist`, `dz_checker` |
| `community` | Сообщество и контент | `club`, `comments`, `group_chat`, `publications` |
| `education` | Обучение и наставничество | `homework`, `cohort`, `workbook`, `certificate` |
| `commerce` | Биллинг и экономика | `billing`, `points`, `revenue_sharing` |
| `admin` | Операционное управление | `users`, `cohorts`, `analytics`, `deployment` |

### Атомарные permissions

#### Ось Knowledge Access (платформа)

| Permission | Описание | Тиры |
|------------|----------|------|
| `platform:knowledge:read` | Доступ к knowledge-mcp (публичные руководства) | T1+ |
| `platform:guides:read` | Доступ к guides-mcp (программы обучения) | T2+ |
| `platform:guides:standard:read` | Стандартные руководства (IWE-шаблон) | T3+ |
| `platform:guides:personal:read` | Персональные руководства (Pack) | T4+ |
| `platform:digital_twin:read` | Просмотр своего ЦД | T1+ (ограниченный), T2+ (полный) |
| `platform:digital_twin:write` | Запись в ЦД (самооценка, цели) | T3+ |
| `platform:digital_twin:export` | Экспорт данных (GDPR) | T1+ |
| `platform:gateway:access` | Доступ к Knowledge Gateway (remote MCP) | T2+ |
| `platform:gateway:personal_kb:read` | Личная база знаний через Gateway | T4+ |
| `platform:gateway:personal_kb:write` | Запись в личную базу через Gateway | T4+ |

#### Ось AI (ИИ-системы)

| Permission | Описание | Тиры |
|------------|----------|------|
| `ai:consultant:use` | Q&A по руководствам (R3) | T1+ (базовый), T2+ (полный) |
| `ai:navigator:use` | Навигатор траектории (R27) | T2+ |
| `ai:diagnostician:use` | Диагност ступени (R28) | T2+ |
| `ai:dz_checker:use` | Проверка ДЗ (R12) | T2+ |
| `ai:strategist:use` | Стратег — план дня/недели (R1) | T3+ |
| `ai:extractor:use` | Экстрактор знаний (R2) | T4+ |
| `ai:tailor:use` | Персональные рекомендации (R27 Tailor) | T3+ |
| `ai:orchestrator:use` | Оркестратор программы (R22) | T3+ |

#### Ось Community (сообщество)

| Permission | Описание | Тиры |
|------------|----------|------|
| `community:club:read` | Чтение клуба (Discourse) | T1+ |
| `community:club:post` | Создание постов в клубе | T2+ |
| `community:club:comment` | Комментирование в клубе | T1+ |
| `community:group_chat:enter` | Вход в групповой чат (семинар/поток) | T2+ (по оплате семинара) |
| `community:publications:read` | Чтение публикаций | T1+ |
| `community:publications:create` | Создание публикаций | T3+ |

#### Ось Education (обучение)

| Permission | Описание | Тиры |
|------------|----------|------|
| `education:homework:submit` | Сдача ДЗ | T2+ |
| `education:homework:review` | Проверка ДЗ (наставник) | TM1+ |
| `education:homework:grade` | Оценка ДЗ (наставник) | TM2+ |
| `education:workbook:read` | Просмотр рабочей тетради | T2+ |
| `education:workbook:write` | Заполнение рабочей тетради | T2+ |
| `education:cohort:view` | Просмотр своего потока | T2+ |
| `education:cohort:manage` | Управление потоком (куратор) | TM3+ / TA2+ |
| `education:certificate:view` | Просмотр сертификатов | T2+ |
| `education:certificate:issue` | Выдача сертификатов | TA3+ |
| `education:seminar:access` | Доступ к семинару (JWT-ссылка, ADR-016) | T2+ (по оплате) |

#### Ось Commerce (биллинг и экономика)

| Permission | Описание | Тиры |
|------------|----------|------|
| `commerce:billing:view_own` | Просмотр своих оплат | T1+ |
| `commerce:billing:pay` | Совершение оплаты | T1+ |
| `commerce:billing:manage` | Управление подписками (CRM) | TA2+ |
| `commerce:billing:refund` | Возвраты | TA3+ |
| `commerce:points:view` | Просмотр баллов | T2+ |
| `commerce:points:earn` | Начисление баллов | T2+ |
| `commerce:points:spend` | Трата баллов | T2+ |
| `commerce:revenue:view` | Просмотр выплат автору | T3+ (автор) |

#### Ось Admin (операции)

| Permission | Описание | Тиры |
|------------|----------|------|
| `admin:users:view` | Просмотр списка пользователей | TA1+ |
| `admin:users:manage` | Управление пользователями (блок, смена тира) | TA2+ |
| `admin:cohorts:create` | Создание потоков | TA2+ |
| `admin:cohorts:assign_mentor` | Назначение наставников | TA3+ |
| `admin:analytics:view` | Просмотр аналитики | TA1+ |
| `admin:analytics:export` | Экспорт аналитики | TA3+ |
| `admin:deployment:manage` | Деплой и мониторинг | TD1 |
| `admin:config:manage` | Настройки платформы | TD1 |

### Role-groups (бандлы permissions → Keto relations)

| Role-group | Permissions (бандл) | Кто получает |
|------------|-------------------|-------------|
| `subscriber:t1` | `platform:knowledge:read`, `platform:digital_twin:read` (limited), `ai:consultant:use` (basic), `community:club:read`, `community:club:comment`, `commerce:billing:view_own`, `commerce:billing:pay` | T1 пользователи |
| `subscriber:t2` | subscriber:t1 + `platform:guides:read`, `platform:gateway:access`, `ai:navigator:use`, `ai:diagnostician:use`, `ai:dz_checker:use`, `community:club:post`, `education:homework:submit`, `education:workbook:*`, `education:cohort:view`, `commerce:points:*` | T2 пользователи |
| `subscriber:t3` | subscriber:t2 + `platform:guides:standard:read`, `platform:digital_twin:write`, `ai:strategist:use`, `ai:tailor:use`, `ai:orchestrator:use`, `community:publications:create`, `commerce:revenue:view` | T3 пользователи |
| `subscriber:t4` | subscriber:t3 + `platform:guides:personal:read`, `platform:gateway:personal_kb:*`, `ai:extractor:use` | T4 пользователи |
| `mentor:tm1` | `education:homework:review` (read-only, scope: one cohort) | TM1 |
| `mentor:tm2` | mentor:tm1 + `education:homework:grade` (scope: own cohorts) | TM2 |
| `mentor:tm3` | mentor:tm2 + `education:cohort:manage` (scope: program) | TM3 |
| `admin:ta1` | `admin:users:view`, `admin:analytics:view` | TA1 |
| `admin:ta2` | admin:ta1 + `admin:users:manage`, `admin:cohorts:create`, `commerce:billing:manage` | TA2 |
| `admin:ta3` | admin:ta2 + `admin:cohorts:assign_mentor`, `admin:analytics:export`, `commerce:billing:refund`, `education:certificate:issue` | TA3 |
| `developer:td1` | all admin + `admin:deployment:manage`, `admin:config:manage` | TD1 |

### Позиции (presets) — ADR-014

| Позиция | = Role-group + Scope |
|---------|---------------------|
| **Ученик T2** | subscriber:t2, scope: enrolled programs |
| **Наставник потока** | subscriber:t2 + mentor:tm2, scope: `cohort:X` |
| **Старший наставник** | subscriber:t3 + mentor:tm3, scope: `program:Y` |
| **Куратор** | subscriber:t2 + admin:ta2, scope: `program:Y` |
| **Владелец** | subscriber:t4 + admin:ta3 + developer:td1, scope: `global` |

### Фаза внедрения

| Фаза | Что | Когда |
|------|-----|-------|
| **A (MVP)** | `education:seminar:access` + `community:group_chat:enter` — семинары как пилот | W15-16 |
| **B** | `platform:gateway:access` + `ai:*:use` — Knowledge Gateway + ИИ-системы | После Ory SSO |
| **C** | `education:homework:*` + `mentor:*` — наставники и потоки | С Web App |
| **D** | `commerce:*` + `admin:*` — полный биллинг и админка | С CRM |

### Keto relation tuples (примеры Фазы A)

```
// Пользователь user:123 — подписчик T2
platform:subscribers#member@user:123

// Группа subscribers включает permission на семинары
education:seminar:*#access@platform:subscribers#member

// Конкретный семинар — доступ по оплате
education:seminar:sem-2026-04-15#access@user:123

// Группа subscribers включает вход в чат
community:group_chat:*#enter@platform:subscribers#member

// Конкретный чат семинара
community:group_chat:chat-sem-2026-04-15#enter@user:123
```

---

## Итоги встреч (заполняется по факту)

### Встречи 1-3 (29 мар — 5 апр)

| # | Вопрос | Решение | Дата |
|---|--------|---------|------|
| 1 | URL Ory / Keto | ⏳ R1 Ory верифицирована (5 апр). Keto URL — ждём Пашу | 5 апр |
| 2 | Gate T2+: Keto | ✅ Keto: атомарные permissions → роли (subscribers). Начать с семинаров, потом остальное | 5 апр |
| 3 | Gateway: merge/score/фильтрация | ✅ Gateway = прозрачный прокси. Не фильтрует, не нормализует. Порог -- на стороне LLM/клиента | 5 апр |
| 4 | Knowledge base разделение | ✅ Личная, проектная, публичная -- разные репо, один способ работы. Gateway = окно. Командная -- на платформе | 5 апр |
| 5 | GDPR / Репликация RU↔EU | ⏸️ Отложено. Олег предупредил о рисках. Нужна юридическая консультация | 5 апр |
| 6 | Новый сервер | ⏳ Андрей после Ory | 5 апр |
| Q-keto | Перечень permissions | 🔶 Карта проработана (6 апр): 6 namespaces, ~45 permissions, 11 role-groups. Ревью на встрече 4 | 6 апр |
| Q-monolith | Декомпозиция монолита | Начинаем с Payment Registry. Обкатка новой архитектуры | 5 апр |
| Q-billing | Activity Hub billing adapter | ✅ Формат в §3.10 (5 типов), паттерн ADR-IWE-005 | 6 апр |

### Встреча 4 (7 апр) — заполнить по факту

| # | Вопрос | Решение | Дата |
|---|--------|---------|------|
| 1 | Ory: auth.aisystant.com статус, Keto URL | | 7 апр |
| 2 | Q-keto: ревью карты permissions (6 ns, 45 perm, 11 roles) | | 7 апр |
| 7a | GitHub App Setup URL — автоматизация? | | 7 апр |
| 7b | ADR-IWE-004 валидация (GitHub App Token 1h TTL) | | 7 апр |
| 8a | Event Bus: direct INSERT vs HTTP | | 7 апр |
| 8b | Контракт ingest_event — 5 типов достаточно? | | 7 апр |
| Р4 | Identity hub через Ory (Фаза B) | | 7 апр |
| Б5 | Каналы для команд (SC-8) | | 7 апр |
| 6 | Новый сервер — сроки, что первым | | 7 апр |

---

*Создано: 2026-04-01. Обновлено: 2026-04-07. История решений: [встреча 1+2 → архив](../0.99.Archive/WP-73-architect-agenda-2-knowledge-gateway.md)*
