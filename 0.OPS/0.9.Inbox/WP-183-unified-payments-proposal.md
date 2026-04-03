# Единый учёт оплат и автоматизация допуска

> **Proposal для обсуждения с командой.**
> **Участники ревью:** Дима (Aisystant), Гиляна (бухгалтерия), Алёна (маркетинг), Юля (декан), Ильшат (менеджмент), Церен и Андрей (архитектура).
>
> **Связанные документы в этой папке:**
> - [WP-183 CRM+Billing Architecture](WP-183-crm-billing-architecture-proposal.md) — архитектура CRM, Directus, Billing Service
> - [WP-115 Сценарий семинара](WP-115-seminar-payment-access-scenario.md) — E2E: оплата → допуск → видео → маршрутка
> - [WP-73 Архитектура платформы](WP-73-aisystant-platform-architecture.md) — §2.9 Биллинг, каналы оплаты
> - [WP-74 Концепция использования](WP-74-platform-concept-of-use.md) — SC-12 Подписка и оплата
> - [WP-109 Activity Hub](WP-109-activity-hub-lms-integration-proposal.md) — Billing adapter, события оплат

---

<details open>
<summary><b>1. Проблема: два мира</b></summary>

Сейчас оплаты хранятся в двух несвязанных базах. Бот не знает об оплатах через Tilda/Монету. Бухгалтер и маркетолог не видят оплаты бота. Декан и преподаватели не видят наполняемость групп. Нет единого окна.

```
МИР 1: Aisystant (Java LMS)              МИР 2: Бот (Python)
├─ YooKassa (подписки, потоки)            ├─ YooKassa (семинары витрины)
├─ Paybox                                 ├─ TG Stars (семинары)
├─ Stripe (Aisystant Corp)                └─ Neon: seminar_payments
├─ Монета/PayAnyWay
├─ Tilda/Ecwid
└─ Aisystant PostgreSQL

         ╳ НЕ СВЯЗАНЫ ╳
```

**Последствия:**
- Оплата через Tilda → Алёна вручную отправляет invite → задержка, ошибки
- Гиляна не видит оплаты через бота (Stars, ЮКасса семинаров)
- Маршрутка (кик неоплативших) невозможна — бот не знает всех оплативших
- Юля и преподаватели не видят наполняемость потоков и семинаров в реальном времени
- Нет единого MRR/LTV — данные в разных местах

</details>

<details open>
<summary><b>2. Полная карта каналов оплаты (as-is)</b></summary>

### 8 каналов, 3 получателя

| # | Канал | Юрисдикция | Получатель | Обработка | Хранение | Бот знает? |
|---|-------|-----------|------------|-----------|----------|------------|
| 1 | **YooKassa** (подписки, потоки) | РФ | ООО | Aisystant LMS | Aisystant PG | Через API (pull, cache 5мин) |
| 2 | **Paybox** | РФ | ООО | Aisystant LMS | Aisystant PG | Нет |
| 3 | **Stripe** | Мир | Aisystant Corp (USA) | Aisystant LMS | Aisystant PG | Нет |
| 4 | **Монета/PayAnyWay** | РФ+СНГ+Мир | ООО | Aisystant LMS | Aisystant PG | Нет |
| 5 | **Tilda + Ecwid** (витрина сайта) | РФ | ООО | Aisystant LMS | Aisystant PG | Нет |
| 6 | **YooKassa** (семинары бота) | РФ | ООО | Python бот | Neon | Да |
| 7 | **TG Stars** (семинары бота) | Глобально | Telegram | Python бот | Neon | Да |
| 8 | **Manual** (B2B, юрлица) | Любая | Любое | Вручную | Нигде | Нет |

### 3 получателя платежей

| Получатель | Юрисдикция | Каналы | Валюта |
|------------|-----------|--------|--------|
| ООО (РФ) | Россия | YooKassa, Paybox, Монета, Tilda | RUB |
| Aisystant Corp | США | Stripe | USD/EUR |
| Telegram | Глобально | TG Stars | XTR (выплата через TON) |

### Что покупают

| Продукт | Каналы оплаты | Тип |
|---------|---------------|-----|
| Подписка БР | YooKassa, Stripe, Paybox, Монета | Рекуррент |
| Поток (интернатура) | YooKassa, Stripe, Paybox, Монета, Tilda | Разовая |
| Семинар (витрина бота) | YooKassa (бот), TG Stars | Разовая |
| Семинар (витрина Tilda) | YooKassa (через Aisystant), Монета, Tilda | Разовая |
| B2B (юрлица) | Manual (счёт + акт) | Разовая |

</details>

<details open>
<summary><b>3. Целевая схема (to-be, с Ory)</b></summary>

**Принципы:**
- **Не дублировать данные** — каждый source-of-truth остаётся на месте
- **Ory = единый identity** — один `ory_id` связывает telegram_id, email, aisystant_id
- **Ory Keto = единый access control** — проверка доступа к чатам, функциям, контенту

### Единый identity (Ory Kratos)

```
Ory Kratos Identity (ory_id: UUID)
  ├─ email (trait)              ← регистрация на сайте
  ├─ telegram_id (trait)        ← /start в боте
  ├─ aisystant_id (trait)       ← миграция из LMS
  └─ tier: T0/T1/T2/T3/T4      ← Ory metadata
```

Ory заменяет ручную склейку `/link`. При регистрации на сайте или в боте — один identity. Все каналы оплаты видят одного человека.

### Архитектура

```
                         Ory Kratos (identity)
                         Ory Keto (access control)
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            Aisystant PG     Neon        Directus
            (каналы 1-5)   (каналы 6-7)  (CRM UI)
                    │           │           │
                    └─────┬─────┘           │
                          ▼                 │
                    Metabase (аналитика) ◄───┘
                          │
                          ├─► Гиляна: все оплаты, сверка
                          ├─► Алёна: воронка T0→T4, конверсия, когорты
                          ├─► Юля: наполняемость потоков и семинаров
                          └─► Преподаватели: списки участников

              Activity Hub (WP-109)
                          │
                          └─► Billing adapter: платёж = событие
                              → engagement → ЦД → аналитика

Бот (допуск в чаты):
  ├─ Ory Keto: check(ory_id, "access", "chat:seminar_iwe")
  ├─ Fallback: Neon seminar_payments (если Keto ещё не развёрнут)
  └─ Webhook от Aisystant (push) → запись оплаты + Keto grant
```

### Воронка входа (для маркетинга)

```
T0 (анонимный)
  │ /start в боте или заход на сайт
  │ → Ory Kratos создаёт identity
  ▼
T1 (зарегистрирован, без подписки)
  │ Trial 30 дней — полный доступ T2–T4
  │ → бесплатные семинары, марафон
  ▼
T2 (подписка БР)
  │ Оплата: YooKassa / Stripe / Монета / Stars
  │ → Keto grant: tier=T2
  │ → доступ: лента, консультации, заметки, планы
  ▼
T3 (ЦД подключён)
  │ Бесплатно — заполнить цифровой двойник
  │ → Keto grant: tier=T3
  ▼
T4 (экзокортекс)
  │ Бесплатно — setup.sh / Gateway URL
  │ → Keto grant: tier=T4
```

**Metabase считает по Ory:** сколько на каждом тире, конверсия T0→T1→T2, retention, churn.

### Допуск в чаты (автоматизация через Keto)

| Событие | Механизм | Действие |
|---------|----------|----------|
| Оплата семинара через бот | Бот записывает + Keto grant `access:chat:{chat_id}` | Invite + видео мгновенно |
| Оплата семинара через Tilda/Монету | Webhook → бот записывает + Keto grant | Invite + видео мгновенно |
| Оплата подписки БР | Keto grant `tier:T2` | Approve join request в Сообщество IWE |
| B2B (manual) | Менеджер в Directus → Keto grant | Approve |
| **Маршрутка (кик)** | Cron: Keto check → нет grant → кик | Предупреждение → 3 дня → кик |
| Отмена подписки / истечение | Keto revoke `tier:T2` | Предупреждение → grace 7 дней → кик из Сообщества |

### Webhook-контракт (Aisystant → бот)

```
POST https://aistmebot-production.up.railway.app/webhook/workshop-payment
Header: X-Webhook-Secret: {WORKSHOP_WEBHOOK_SECRET}
Content-Type: application/json

{
  "ory_id": "uuid",              // единый identity (предпочтительно)
  "telegram_id": 123456789,      // fallback если Ory ещё не мигрирован
  "purpose": "SEMINAR",          // WORKSHOP | SEMINAR | INTERNSHIP
  "seminar_code": "SE-2026.2-T", // код семинара (для SEMINAR)
  "amount": 5000,
  "currency": "RUB",
  "payment_id": "yookassa_xxx",  // idempotency key
  "source": "tilda"              // tilda | moneta | yookassa | stripe | paybox
}
```

**Переходный период (до полного Ory):** бот принимает и `ory_id`, и `telegram_id`. Когда Ory полностью развёрнут — `telegram_id` извлекается из Ory traits по `ory_id`.

</details>

<details open>
<summary><b>4. Этапы реализации</b></summary>

### Фаза A: Единый учёт (можно без Ory)

| # | Что | Кто | Dep | Бюджет | Результат |
|---|-----|-----|-----|--------|-----------|
| 0 | **Этот proposal** — согласование с командой | Все | — | 1h | Единое понимание |
| 1 | **Directus на Railway** + Neon datasource | Tseren | — | 2h | Гиляна/Алёна/Юля видят оплаты бота |
| 2 | **Directus + Aisystant PG** (read-only) | Tseren + Дима | Дима: доступ к PG | 2h | Единое окно всех оплат |
| 3 | **Metabase на Railway** + дашборды воронки | Tseren | Этап 1 | 3h | MRR, LTV, воронка T0→T4, наполняемость |
| 4 | **Webhook Aisystant → бот** | Дима | Контракт (§3) | 2h | Авто-invite при оплате через Tilda/Монету |
| 5 | **Маршрутка** (cron-кик неоплативших) | Tseren | Этап 4 | 2h | Чат = только оплатившие |
| 6 | **Manual-оплаты** через Directus | Tseren | Этап 1 | 1h | B2B через CRM |

**Бюджет Фазы A:** ~13h. Критический путь: Этапы 2 и 4 (dep: Дима). Без Димы: этапы 1, 3, 6 параллельно.

### Фаза B: Ory integration (после WP-187)

| # | Что | Кто | Dep | Бюджет | Результат |
|---|-----|-----|-----|--------|-----------|
| 7 | **Ory Keto** — ACL для доступа к чатам и функциям | Tseren + Дима | WP-187 (Ory Kratos deployed) | 4h | Единый access control |
| 8 | **Миграция identity** — связка telegram_id ↔ ory_id для всех пользователей | Tseren + Дима | Этап 7 | 2h | Одна identity на человека |
| 9 | **Бот → Keto** — замена проверок подписки/оплаты на Keto check | Tseren | Этап 7 | 3h | Допуск через Keto, не через API/таблицы |
| 10 | **Directus SSO через Ory** | Tseren | Этап 7 | 1h | Единый логин для Гиляны/Алёны/Юли |

**Бюджет Фазы B:** ~10h. Dep: WP-187 (Ory Kratos deployed + Keto ready).

### Фаза C: Экономика (после Фаз A+B)

| # | Что | Кто | Dep | Бюджет | Результат |
|---|-----|-----|-----|--------|-----------|
| 11 | **Баллы** (Points Engine, WP-121) | Tseren | Фаза B | 6h | Начисление за активность, списание за семинары/курсы |
| 12 | **Revenue Sharing** | Tseren | Фаза A | 3h | Platform 30% / Author 50% / Instructor 15% / Curator 5% |
| 13 | **Юнит-экономика в Metabase** | Tseren | Фаза A | 2h | CAC, LTV, churn по каналам и продуктам |

**Бюджет Фазы C:** ~11h.

</details>

<details open>
<summary><b>5. Вопросы для обсуждения</b></summary>

### Для Димы (Aisystant)

1. **Read-only доступ к Aisystant PG** для Directus — как организовать? Отдельный PG-пользователь с SELECT-only? VPN или публичный endpoint?
2. **Webhook при оплате** workshop/семинара → `POST` на бот (контракт в §3) — какая сложность? Одна функция в `AccessService.java` после `addOrExtendAccess()`?
3. **Монета/PayAnyWay** — оплаты проходят через LMS Aisystant и хранятся в той же PG?
4. **telegram_id при оплате через Tilda** — Aisystant знает связку `email ↔ telegram_id`? Если нет — как находить?

### Для Гиляны (бухгалтерия)

5. Какие **отчёты** нужны? MRR, ARR, LTV, выгрузка оплат за период?
6. Нужна ли **сверка** между каналами (YooKassa выписка vs Aisystant БД vs бот)?
7. Как сейчас учитываются оплаты через **Aisystant Corp** (Stripe, USD)?

### Для Алёны (маркетинг)

8. Какие **разрезы** для маркетинга? По каналам привлечения, когортам, продуктам, географии?
9. Нужна ли **воронка** (лид → оплата → в чате → активный)?
10. **CAC** (стоимость привлечения) — откуда данные по расходам на рекламу?

### Для Юли (декан)

11. Какая информация по **наполняемости групп** нужна? Количество записавшихся, оплативших, активных?
12. **Преподаватели** — нужен ли им доступ к спискам участников своих потоков? Через Directus (RBAC) или через отдельный отчёт?

### Для Ильшата (менеджмент)

13. Какие **операционные метрики** нужны? Количество оплат за день/неделю, задержки в выдаче доступа?
14. Как сейчас устроен **процесс ручного допуска** при B2B-оплатах?
15. Нужен ли **helpdesk** (тикет-система для обращений по оплатам, доступам, рефандам)? Если да — отдельный инструмент или канал в Directus/Telegram?

### Для Церена и Андрея (архитектура)

16. **Баллы (Points Engine, WP-121):** как связать с единым учётом? Баллы = альтернативная оплата (1 балл = 1₽). Начисление за активность, списание за семинары/курсы. Нужна таблица `finance.point_transactions` в Neon?
17. **Юнит-экономика:** Revenue Sharing (Platform 30% / Author 50% / Instructor 15% / Curator 5%) — считать в Metabase или в Billing Module?
18. **Activity Hub (WP-109):** Billing adapter — каждый платёж = событие `payment_completed`. Реализовать в Фазе 0 AH или отдельно?
19. **Ory Keto ACL-модель:** какие relation tuples? `user:ory_id#access@chat:seminar_iwe`, `user:ory_id#tier@platform:T2`? Или плоская модель?

</details>

<details>
<summary><b>6. Связь с другими РП</b></summary>

| РП | Как связано |
|-----|------------|
| **WP-73** | §2.9 Биллинг — обновить таблицу каналов |
| **WP-74** | SC-12 — дополнить: витрина бота, deep links, маршрутка |
| **WP-109** | Activity Hub — Billing adapter: каждый платёж = событие |
| **WP-115** | Полный E2E сценарий семинара: маркетинг → оплата (бот/сайт) → авто-допуск в чат (3-5 сек) → маршрутка (кик неоплативших) → видео (JWT Kinescope). Реализация витрины (showcase.py) покрывает оплату+допуск; остаётся: маршрутка, JWT-видео, HMAC в deep links |
| **WP-181** | Воронка чатов — webhook от Aisystant разблокирует авто-invite |
| **WP-183** | CRM+Billing — этот proposal = расширение WP-183 |
| **WP-188** | Маркетинг — Metabase дашборды, CAC tracking |
| **WP-194** | Подписка БР — ценообразование |
| **WP-121** | Points Engine — баллы как альтернативная оплата, начисление за активность |
| **WP-187** | Ory (Kratos + Keto) — единый identity + access control. Фаза B зависит от WP-187 |
| **WP-198** | Бот-вышибала — маршрутка: cron-кик |

</details>

---

*Создано: 2026-04-03. Для обсуждения на ближайшей оперативке.*
