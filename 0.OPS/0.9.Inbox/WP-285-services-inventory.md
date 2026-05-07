---
type: inventory
title: "Список сервисов: Track A → Track B"
status: draft
created: 2026-05-07
author: Церен
---

# Список сервисов: что есть и что нужно на мировой платформе

> **Track A (Россия)** — работает как есть, ничего не трогаем.
> **Track B (Мир)** — новый независимый деплой. Каждый сервис получает свою копию.
> «Дублировать» = развернуть новый инстанс с тем же кодом, но указывающий на Track B инфраструктуру (Cloud SQL, Ory EU, Stripe).

---

<details open>
<summary><b>5. Итог: приоритет для старта 18 мая</b></summary>

Минимальный набор, чтобы хотя бы один пользователь смог зарегистрироваться и начать работу:

1. **GKE кластер + Cloud SQL** — Паша (18 мая)
2. **Ory EU** — авторизация без него ничего не работает
3. **gateway-mcp** — точка входа в платформу
4. **event-gateway** — без него события не пишутся
5. **aist_bot_newarchitecture** — основной интерфейс пользователя
6. **БД: persona, journal, subscription** — три ключевые для онбординга

Остальные можно поднимать итеративно после первого пользователя.

</details>

<details>
<summary><b>1. CF Workers (Cloudflare) — 11 сервисов</b></summary>

Все работают на Cloudflare Workers. Код тот же, меняются только переменные окружения (DATABASE_URL, ORY_URL, STRIPE_KEY и т.д.).

| Сервис | Что делает | Track A | Track B | Примечания |
|--------|-----------|---------|---------|------------|
| **gateway-mcp** | API-шлюз: OAuth, роутинг по доменам, MCP-точка входа | `mcp.aisystant.com` | новый домен (TBD) | Обновить Hyperdrive binding → Cloud SQL |
| **knowledge-mcp** | Поиск по базе знаний (Pack, guides, SOTA, граф концептов) | Neon #7 knowledge | Cloud SQL knowledge | Переиндексировать граф под EN-контент |
| **personal-knowledge-mcp** | Личная база знаний пользователя (заметки, эмбеддинги) | Neon #1 persona | Cloud SQL persona | Обновить строку подключения |
| **digital-twin-mcp** | Показатели, состояния, прогресс ученика | Neon #5 indicators | Cloud SQL indicators | Обновить строку подключения |
| **guides-mcp** | Каталог программ и руководств | Neon #8 reference | Cloud SQL reference | Загрузить EN-программы |
| **event-gateway** | Единственный writer событий в journal | Neon #2 journal | Cloud SQL journal | Обновить строку подключения |
| **fsm-mcp** | Конечный автомат ассистента ученика | stateless | stateless | Переменные среды под Track B |
| **payment-receiver** | Webhook от платёжных систем | YooKassa | **Stripe только** | Новый handler для Stripe webhooks |
| **observability-webhook** | Better Stack → TG-алерты об инцидентах | stateless | stateless | Новый TG-бот / чат для Track B |
| **status-proxy** | Редирект на страницу статуса платформы | `status.aisystant.com` | новый домен | Обновить CNAME |
| **google-drive-mcp** | Интеграция с Google Drive | stateless (OAuth) | stateless (OAuth) | Проверить OAuth credentials |

**Что нужно сделать общее:** создать новый `wrangler.toml` или `.env` под Track B для каждого воркера. Деплоить в тот же Cloudflare-аккаунт, но с другими именами и привязками.

</details>

<details>
<summary><b>2. Python-сервисы (контейнеры) — 5 сервисов</b></summary>

Сейчас живут на Railway. Для Track B: GKE Standard (K8s Deployment или CronJob).

| Сервис | Что делает | Track A | Track B | Тип |
|--------|-----------|---------|---------|-----|
| **aist_bot_newarchitecture** | Telegram-бот (@aist_me_bot, @aist_pilot_me) | Railway | GKE Deployment | Deployment |
| **multi-domain-projection-worker** | Проекции событий → persona / subscription / indicators | Railway / VPS | GKE CronJob | CronJob |
| **rewards-projection-worker** | Расчёт баллов и достижений | Railway / VPS | GKE CronJob | CronJob |
| **activity-hub** | Сборщик событий (medallion: bronze/silver/gold) | VPS? | GKE Deployment | Deployment |
| **payment-registry** | Единый журнал транзакций | VPS? | GKE Deployment | Deployment |

**Не переносить на Track B:**
- **bridge-2-events-poller** — polling legacy LMS Aisystant. Legacy LMS только российская, для Track B не нужен.

**Что нужно сделать общее:** каждому сервису — Dockerfile (если нет) + Werf-манифест + K8s manifest (env vars из Secret, указывающие на Cloud SQL, Ory EU).

</details>

<details>
<summary><b>3. Базы данных — 12 Neon → 12 Cloud SQL</b></summary>

Track A: остаются в Neon как есть. Track B: новые инстансы в Cloud SQL (europe-west4, тот же регион что кластер).

| # | БД | Что хранит | Track B — что сделать |
|---|----|-----------|----------------------|
| 1 | **persona** | Аккаунты, настройки, личные заметки, эмбеддинги | Создать схему, пустая |
| 2 | **journal** | Все события платформы (event sourcing) | Создать схему, пустая |
| 3 | **payment** | Платежи, возвраты, методы оплаты | Создать схему + **добавить Stripe-поля** |
| 4 | **subscription** | Подписки, автопродления, аудит | Создать схему, пустая |
| 5 | **indicators** | Показатели, baseline, снапшоты прогресса | Создать схему, пустая |
| 6 | **learning** | Курсы, прогресс, задания, менторинг | Создать схему + загрузить EN-контент |
| 7 | **knowledge** | Граф концептов, индексы, эмбеддинги | Создать схему + переиндексировать |
| 8 | **reference** | Тарифы, программы, справочники | Создать схему + **загрузить мировые тарифы** |
| 9 | **publication** | Статьи, посты, каналы публикаций | Создать схему, пустая |
| 10 | **community** | Наставничество, встречи, группы | Создать схему, пустая |
| 11 | **lead** | Лиды, UTM-визиты, воронка | Создать схему, пустая |
| 12 | **rewards** | Баллы, достижения, квалификации | Создать схему + **новая эмиссия для Track B** |

**Итог:** Схемы берутся из Neon (pg_dump --schema-only). Данные НЕ мигрируются — Track B стартует пустым. Пользователи Track A могут перейти через экспорт/импорт (WP-285 Ф6).

</details>

<details>
<summary><b>4. Внешние сервисы</b></summary>

| Сервис | Track A | Track B | Что делать |
|--------|---------|---------|-----------|
| **Ory (auth)** | VK Cloud (RU) | GKE EU, отдельный инстанс | Развернуть Ory Kratos + Hydra на GKE, своя БД |
| **Cloudflare** | DNS + Workers + DDoS | Тот же аккаунт | Новые DNS-записи для Track B домена |
| **YooKassa** | Платежи (рубли) | — | **Не нужен на Track B** |
| **Stripe** | — | Платежи (USD/EUR/...) | Зарегистрировать аккаунт, получить ключи |
| **Better Stack** | Мониторинг Track A (10 мониторов) | Новые мониторы для Track B | Добавить monitors + keyword-check для каждого сервиса |
| **Telegram** | Бот @aist_me_bot | Новый бот для Track B | Зарегистрировать нового бота через @BotFather |
| **GitHub** | org: `aisystant` | Новая отдельная организация | Паша создаёт, форкает нужные репо |
| **Terraform Cloud** | — (Track A без него) | IaC для GKE, Cloud SQL, сети | Паша настраивает отдельный репо |
| **Google Cloud** | — | GKE Standard + Cloud SQL | Церен регистрирует аккаунт, $300 кредит |

</details>
