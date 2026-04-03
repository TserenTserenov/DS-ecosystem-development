# Единый учёт оплат и автоматизация допуска

> **Proposal для обсуждения с командой.** Связь: WP-183 (CRM+Billing), WP-181 (воронка чатов), WP-115 (сценарий семинара).
> **Участники ревью:** Дима (Aisystant), Гиляна (бухгалтерия), Алёна (маркетинг), Церен (архитектура).

---

<details open>
<summary><b>1. Проблема: два мира</b></summary>

Сейчас оплаты хранятся в двух несвязанных базах. Бот не знает об оплатах через Tilda/Монету. Бухгалтер и маркетолог не видят оплаты бота. Нет единого окна.

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
- Нет единого MRR/LTV — данные в разных местах

</details>

<details open>
<summary><b>2. Полная карта каналов оплаты (as-is)</b></summary>

### 8 каналов

| # | Канал | Юрисдикция | Юрлицо | Обработка | Хранение | Бот знает? |
|---|-------|-----------|--------|-----------|----------|------------|
| 1 | **YooKassa** (подписки, потоки) | РФ | ООО | Aisystant LMS | Aisystant PG | Через API (pull, cache 5мин) |
| 2 | **Paybox** | РФ | ООО | Aisystant LMS | Aisystant PG | Нет |
| 3 | **Stripe** | Мир | Aisystant Corp (USA) | Aisystant LMS | Aisystant PG | Нет |
| 4 | **Монета/PayAnyWay** | РФ+СНГ+Мир | ООО | Aisystant LMS | Aisystant PG | Нет |
| 5 | **Tilda + Ecwid** (витрина сайта) | РФ | ООО | Aisystant LMS | Aisystant PG | Нет |
| 6 | **YooKassa** (семинары бота) | РФ | ООО | Python бот | Neon | Да |
| 7 | **TG Stars** (семинары бота) | Глобально | — | Python бот | Neon | Да |
| 8 | **Manual** (B2B, юрлица) | Любая | Любое | Вручную | Нигде | Нет |

### 2 юрисдикции / 2 юрлица

| Юрлицо | Юрисдикция | Каналы | Валюта |
|--------|-----------|--------|--------|
| ООО (РФ) | Россия | YooKassa, Paybox, Монета, Tilda | RUB |
| Aisystant Corp | США | Stripe | USD/EUR |

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
<summary><b>3. Целевая схема (to-be)</b></summary>

**Принцип: не дублировать данные.** Каждый source-of-truth остаётся на месте. Directus и Metabase подключаются к обоим.

```
Aisystant PG (source-of-truth)          Neon (source-of-truth)
каналы 1-5: подписки, потоки,           каналы 6-7: семинары бота
Tilda, Монета, Stripe                   seminar_payments
         │                                      │
         │         Directus (Railway)            │
         └────────► два datasource ◄────────────┘
                        │
                        ├─► Гиляна: все оплаты, сверка, выгрузки
                        ├─► Алёна: воронка, конверсия, когорты
                        └─► Менеджер: ручные оплаты B2B
                        │
                   Metabase (Railway)
                        │
                        └─► MRR, LTV, CAC, churn (SQL по обеим БД)

Бот (допуск в чаты):
  ├─ Neon seminar_payments — свои оплаты (каналы 6-7)
  ├─ Aisystant API (pull) — подписки, потоки (каналы 1-5)
  └─ Webhook от Aisystant (push) — оплата через Tilda/Монету/сайт
       └── dep: Дима добавляет HTTP POST в AccessService.java
```

### Допуск в чаты (автоматизация)

| Событие | Как бот узнаёт | Действие |
|---------|----------------|----------|
| Оплата семинара через бот (Stars/ЮКасса) | Сразу (сам обработал) | Invite + видео мгновенно |
| Оплата семинара через Tilda/Монету | Webhook от Aisystant | Invite + видео мгновенно |
| Оплата подписки БР | API `has_active_subscription` (pull, cache 5мин) | Approve join request в Сообщество IWE |
| Оплата вручную (B2B) | Менеджер вносит в Directus → бот проверяет | Approve или admin добавляет |
| **Маршрутка (кик)** | Cron 1 раз/сутки: проверяет обе БД | Предупреждение → 3 дня → кик |

### Webhook-контракт (Aisystant → бот)

```
POST https://aistmebot-production.up.railway.app/webhook/workshop-payment
Header: X-Webhook-Secret: {WORKSHOP_WEBHOOK_SECRET}
Content-Type: application/json

{
  "telegram_id": 123456789,       // обязательно (из связки tg↔aisystant)
  "purpose": "SEMINAR",           // WORKSHOP | SEMINAR | INTERNSHIP
  "seminar_code": "SE-2026.2-T",  // код семинара (для SEMINAR)
  "amount": 5000,
  "currency": "RUB",
  "payment_id": "yookassa_xxx",   // idempotency key
  "source": "tilda"               // tilda | moneta | yookassa | stripe | paybox
}
```

**Если telegram_id неизвестен** (человек не привязан к боту): Aisystant отправляет `aisystant_id` вместо `telegram_id`. Бот сохраняет отложенную оплату. При `/link` (привязка аккаунта) — бот выдаёт invite.

</details>

<details open>
<summary><b>4. Этапы реализации</b></summary>

| # | Что | Кто | Dep | Бюджет | Результат |
|---|-----|-----|-----|--------|-----------|
| 0 | **Этот proposal** — согласование с командой | Все | — | 1h | Единое понимание |
| 1 | **Directus на Railway** + Neon datasource | Tseren | — | 2h | Гиляна/Алёна видят оплаты бота |
| 2 | **Directus + Aisystant PG** (read-only) | Tseren + Дима | Дима: доступ к PG | 2h | Единое окно всех оплат |
| 3 | **Metabase на Railway** + дашборды | Tseren | Этап 1 | 3h | MRR, LTV, воронка |
| 4 | **Webhook Aisystant → бот** | Дима | Контракт (§3) | 2h | Авто-invite при оплате через Tilda/Монету |
| 5 | **Маршрутка** (cron-кик неоплативших) | Tseren | Этап 4 | 2h | Чат = только оплатившие |
| 6 | **Manual-оплаты** через Directus | Tseren | Этап 1 | 1h | B2B через CRM |

**Общий бюджет:** ~13h (без учёта согласований)

**Критический путь:** Этап 2 (dep: Дима) и Этап 4 (dep: Дима). Без Димы: этапы 1, 3, 6 можно делать параллельно.

</details>

<details open>
<summary><b>5. Расхождения в документах (что обновить)</b></summary>

| Документ | Проблема | Действие |
|----------|---------|----------|
| **SC.112** (Billing) | Нет Монеты, Aisystant Corp, Tilda/Ecwid, Paybox | Дополнить таблицу каналов |
| **MAP.002** (сервисы) | Нет сервисов Billing, CRM, Access Manager (SC.112/114 не представлены) | Добавить S-записи |
| **WP-73 §2.9** | Нет Монеты, Aisystant Corp. Q14 (два юрлица) открыт | Дополнить §2.9 + закрыть Q14 |
| **WP-74 SC-12** | Нет витрины бота, deep links, auto-approve, маршрутки. Stars = «донаты» (устарело) | Дополнить SC-12 |
| **WP-115** | Расхождения с реализацией: auto-approve (unban vs invite+join_request), HMAC в deep link (нет), таблицы (seminars vs crm.events) | Синхронизировать с showcase.py |
| **WP-183** | Нет two datasources, Монеты, Aisystant Corp | Дополнить proposal |

</details>

<details open>
<summary><b>6. Вопросы для обсуждения</b></summary>

### Для Димы (Aisystant)

1. **Read-only доступ к Aisystant PG** для Directus — как организовать? Отдельный PG-пользователь с SELECT-only? VPN или публичный endpoint?
2. **Webhook при оплате** workshop/семинара → `POST` на бот (контракт в §3) — какая сложность? Одна функция в `AccessService.java` после `addOrExtendAccess()`?
3. **Монета/PayAnyWay** — оплаты проходят через LMS Aisystant? Есть ли webhook от Монеты → Aisystant?
4. **telegram_id при оплате через Tilda** — Aisystant знает связку `email ↔ telegram_id`? Если нет — как находить telegram_id?

### Для Гиляны (бухгалтерия)

5. Какие **отчёты** нужны? MRR, ARR, LTV, выгрузка оплат за период?
6. Нужна ли **сверка** между каналами (YooKassa выписка vs Aisystant БД vs бот)?
7. Как сейчас учитываются оплаты через **Aisystant Corp** (Stripe, USD)?

### Для Алёны (маркетинг)

8. Какие **разрезы** для маркетинга? По каналам привлечения, когортам, продуктам, географии?
9. Нужна ли **воронка** (лид → оплата → в чате → активный)?
10. **CAC** (стоимость привлечения) — откуда данные по расходам на рекламу?

### Архитектурные (для оперативки)

11. **Q14 из WP-73:** два юрлица (ООО + Aisystant Corp) — как отражать в едином учёте? Один Directus с фильтром по юрлицу?
12. **Paybox** — планируется ли отключение? Или оставляем как резерв?
13. **PayPal** — упоминается в WP-73 как «Мир», но не реализован. Нужен?

</details>

<details>
<summary><b>7. Связь с другими РП</b></summary>

| РП | Что берём | Как связано |
|-----|-----------|------------|
| **WP-73** | Архитектура платформы, §2.9 Биллинг | Обновить таблицу каналов, закрыть Q14 |
| **WP-74** | Сценарии SC-12 | Дополнить: витрина бота, deep links, маршрутка |
| **WP-109** | Activity Hub | Billing adapter — отдельная фаза или часть AH? |
| **WP-115** | Сценарий семинара | Синхронизировать с реализацией showcase.py |
| **WP-181** | Воронка чатов | Webhook от Aisystant разблокирует авто-invite |
| **WP-183** | CRM+Billing | Этот proposal = расширение WP-183 |
| **WP-188** | Маркетинг | Metabase дашборды, CAC tracking |
| **WP-194** | Подписка БР | Ценообразование, контент-серия |
| **WP-198** | Бот-вышибала | Маршрутка: cron-кик, dep:webhook |

</details>

---

*Создано: 2026-04-03. Для обсуждения на ближайшей оперативке.*
