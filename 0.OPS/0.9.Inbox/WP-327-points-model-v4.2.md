---
date: 2026-05-27
status: for-review
wp: WP-327
target: DP.ECON.001 v4.2 + DP.SC.105
version: "v4.2 (peer-calibrated)"
authors: Claude + Kimi (peer-сессия 2026-05-27-14)
reviewer: Ильшат
---

# Модель начисления баллов и бонусов — v4.2

> **Что изменилось относительно v4.1** (peer-сессия с Кими 27 мая 2026):
> - Курс управляется через **EMA(0.3)**, не сырой monthly recalc
> - Добавлены **floor** и **ceiling** на курс
> - **K снижен с 10 до 8** (калибровка под цель 10%)
> - Рефералы вынесены **отдельной статьёй** (5% CAC вне loyalty-бюджета)
> - Добавлен **per_user_monthly_cap** против winner-take-all
> - Бонусный бюджет уточнён: **10% от выручки** (было «до 20%»)

---

## 1. Три системы учёта

| Система | Что считает | Убывает? | Курс к ₽ |
|---|---|---|---|
| **Баллы** | `earned_total` — сумма всех начислений | **Никогда** | Нет |
| **Бонусы** | `min(баллы, Σ(active_days_at_qual_i × daily_cap_i))` | Да (при оплате) | **Есть** |
| **Ступень** | cp-профиль (13 срезов + 7 bh) | Нет | Нет |

**Ключевое правило:** пользователь видит «Баллы: 15 470» (без ₽) и «Бонусы: 700 → скидка 35 ₽». Баллы потратить нельзя. Курс применяется только к бонусам в момент оплаты.

Баллы — сигнал активности и прогресса, который никогда не обесценивается. Бонусы — экономический инструмент со своим курсом и cap'ами. Это разделение снимает проблему «инфляции» при росте платформы.

---

## 2. Бюджетная структура

```
revenue            = N_подписчиков × 1 000 ₽/мес
loyalty_budget     = revenue × 10%   ← основная программа лояльности
referral_budget    = revenue × 5%    ← реферальная программа (отдельная статья CAC)
safety_reserve     = loyalty_budget × 25%
effective_pool     = loyalty_budget × 75%
```

**При N = 500 подписчиков:**

| Статья | Сумма |
|---|---|
| Выручка | 500 000 ₽/мес |
| Loyalty budget (10%) | 50 000 ₽/мес |
| Referral budget (5%) | 25 000 ₽/мес |
| Safety reserve (25% от loyalty) | 12 500 ₽/мес |
| **Effective pool** | **37 500 ₽/мес** |
| Target emission (при rate=0.05) | 750 000 бонусов/мес |

**Важно:** рефералы — отдельная статья маркетингового бюджета (CAC). Они не уменьшают loyalty_budget для действующих пользователей.

---

## 3. Курс бонусов (rate ₽/бонус)

### Стартовый курс

**rate = 0.05 ₽/бонус** — установлен вручную из расчёта N=500.

### Механизм обновления (EMA)

```
rate_new = rate_prev × (1 − α) + rate_raw × α
rate_raw = effective_pool / total_bonuses_emitted_prev_month
α = 0.3   (память ~3–4 месяца)

rate_new = clamp(rate_new, floor, hard_ceiling)
floor        = 0.01 ₽/бонус   ← минимальная ценность бонуса
hard_ceiling = 0.20 ₽/бонус   ← защита первых месяцев с малой эмиссией
```

**Почему EMA, а не прямой пересчёт:**
Сырой monthly recalc создаёт волатильность — при вирусном росте в январе rate обвалится в феврале. EMA сглаживает: пользователь не видит резких изменений, курс меняется плавно.

**Пересмотр:** 1-е число каждого месяца. На UI: «Курс на июнь: 0.05 ₽/бонус. Пересматривается 1 июля.»

---

## 4. Формула начисления баллов

### Тип А — С effort (временем)

Действия, где время = содержательный вклад: `lesson_completed`, `wp_completed`, `coding_time`, `text_submitted`, `content_published` и др.

```
effort_factor = effort_minutes ^ 0.6
base          = effort_factor × rarity_mult × group_mult
```

### Тип Б — Маркерные (без времени)

Действие зафиксировано, время не значимо: `pomodoro_completed`, `git_commit`, `club_like_created`, `club_invite_accepted`, `pack_updated` и др.

```
marker_base   = 1   (единый для всех маркерных)
base          = marker_base × rarity_mult × group_mult
```

### Общая формула

```
raw                   = base × qual_mult × streak_mult
effective_per_action  = LEAST(raw, action_cap)

daily_sum            += effective_per_action
if daily_sum > daily_total_cap:
    effective_per_action = 0   # или остаток до daily_total_cap
```

| Параметр | Значение / Источник |
|---|---|
| `effort_minutes` | Экспертная оценка («урок = 45 мин») или WakaTime |
| `rarity_mult` | `clamp((median_cnt_90d / cnt_this_type)^0.3, 0.5, 3.0)` — snapshot раз в месяц |
| `group_mult` | G1=1, G2=2, G3=3, G4=4 |
| `qual_mult` | Таблица ниже |
| `streak_mult` | ×1.0 … ×2.0 (мягкий сброс) |
| `action_cap` | `200 × qual_mult` |
| `daily_total_cap` | `action_cap × K`, **K = 8** (конфиг, не хардкод) |
| `per_user_monthly_cap` | ~3 000 бонусов/мес — защита от winner-take-all |

---

## 5. Таблицы активностей

> **effective** рассчитан для Ученика МИМ (qual_mult=1.0, action_cap=200) со страйком 7 дней (×1.2), rarity=1.0.

### G1 — Личное (group_mult = 1)

| event_type | Описание | effort_min | max_per_day | effective |
|---|---|:---:|:---:|:---:|
| `pomodoro_completed` | Помодоро завершён | маркер | 2 | 1.2 |
| `lesson_completed` | Урок завершён | 45 мин | 2 | 11.1 |
| `note_to_capture` | Заметка захвачена | маркер | 2 | 1.2 |
| `training_attempt` | Попытка тренировки | 30 мин | 3 | 8.2 |
| `ai_chat` | Чат с ИИ | маркер | 3 | 1.2 |
| `slot_logged` | Саморазвитие-слот | 30 мин | 2 | 8.2 |
| `marathon_step` | Шаг марафона | маркер | 2 | 1.2 |
| `test_passed` | Тест пройден | 15 мин | 1 | 5.0 |
| `club_like_created` | Лайк поставлен | маркер | 1 | 1.2 |
| `feed_completed` | Лента прочитана | маркер | 1 | 1.2 |

### G2 — Продукт (group_mult = 2)

| event_type | Описание | effort_min | max_per_day | effective |
|---|---|:---:|:---:|:---:|
| `git_commit` | Git-коммит | маркер | 1 | 2.4 |
| `iwe_session` | IWE-сессия проведена | маркер | 3 | 2.4 |
| `coding_time` | Время кодинга (WakaTime, 60 мин) | 60 мин | 1 | 27.2 |
| `text_submitted` | Текст сдан | 30 мин | 2 | 16.3 |
| `table_submitted` | Таблица сдана | 30 мин | 2 | 16.3 |
| `content_published` | Контент опубликован | 120 мин | 1 | 42.2 |
| `wp_completed` | Рабочий продукт завершён | 240 мин | 1 | 66.7 |
| `workbook_push` | Рабочая книга загружена | маркер | 1 | 2.4 |

### G3 — Знание (group_mult = 3)

| event_type | Описание | effort_min | max_per_day | effective |
|---|---|:---:|:---:|:---:|
| `pack_updated` | Pack обновлён | маркер | 1 | 3.6 |
| `knowledge_extracted` | Знание извлечено в Pack/memory | 60 мин | 1 | 40.8 |
| `task_submitted` | Задание сдано | 20 мин | 2 | 18.0 |
| `learning_completed` | Обучение завершено | 240 мин | 3 | 100.1 |
| `assessment_completed` | Аттестация пройдена | 45 мин | 1 | 33.4 |
| `distinction_added` | Различение добавлено | 30 мин | 2 | 24.5 |
| `method_described` | Метод описан | 60 мин | 1 | 40.8 |

### G4 — Сообщество (group_mult = 4)

| event_type | Описание | effort_min | max_per_day | effective |
|---|---|:---:|:---:|:---:|
| `club_post_created` | Пост в клубе | маркер | 2 | 4.8 |
| `club_topic_created` | Тема в клубе | маркер | 3 | 4.8 |
| `comment_created` | Комментарий | маркер | 3 | 4.8 |
| `club_solution_accepted` | Ответ принят | маркер | 2 | 4.8 |
| `club_invite_accepted` | Реферал принял приглашение | маркер | 2 | 4.8 |
| `club_trust_promoted` | Уровень доверия повышен | маркер | 1 | 4.8 |

---

## 6. Шкала квалификации и qual_mult

`action_cap = 200 × qual_mult`
`daily_total_cap = action_cap × K`, **K = 8** (конфиг)

| # | Уровень | Шкала | qual_mult | action_cap | daily_total_cap (K=8) |
|:---:|---|:---:|:---:|:---:|:---:|
| 1 | Случайный | IWE | ×0.20 | 40 | 320 |
| 2 | Практикующий | IWE | ×0.40 | 80 | 640 |
| 3 | Систематический | IWE | ×0.60 | 120 | 960 |
| 4 | Дисциплинированный | IWE | ×0.80 | 160 | 1 280 |
| 5 | **Проактивный = Ученик МИМ** | IWE = МИМ | **×1.00** | **200** | **1 600** |
| 6 | Работник | МИМ | ×1.30 | 260 | 2 080 |
| 7 | Стратег | МИМ | ×1.60 | 320 | 2 560 |
| 8 | Специалист | МИМ | ×2.00 | 400 | 3 200 |
| 9 | Практик | МИМ | ×2.50 | 500 | 4 000 |
| 10 | Мастер | МИМ | ×3.00 | 600 | 4 800 |
| 11 | Реформатор | МИМ | ×4.00 | 800 | 6 400 |
| 12 | Общественный деятель | МИМ | ×5.00 | 1 000 | 8 000 |

> Ступень читается из Digital Twin. Points Engine только читает, не вычисляет.

**Калибровка K=8 под цель 10%:**

При гипотетическом распределении N=500:
```
Stage 1 (60%): 300 чел × 750 бонусов/мес × 0.2 = 45 000
Stage 2 (25%): 125 чел × 1920 бонусов/мес × 0.4 = 96 000
Stage 3 (10%):  50 чел × 4320 бонусов/мес × 1.0 = 216 000
Stage 4  (4%):  20 чел × 6750 бонусов/мес × 2.0 = 270 000
Stage 5  (1%):   5 чел × 12000 бонусов/мес × 4.0 = 240 000
Σ (K=10) ≈ 867 000 бонусов (+15% к target 750 000)
Σ (K=8)  ≈ 765 000 бонусов ≈ target ✅
```

**K хранится в конфиге** (`loyalty_pool_config` или env var), не хардкод. Обязательный review после первого полного месяца реальных данных.

---

## 7. Множитель систематичности (страйк)

| Серия (дней) | streak_mult |
|:---:|:---:|
| 0–6 | ×1.00 |
| 7–13 | ×1.20 |
| 14–20 | ×1.50 |
| 21–29 | ×1.80 |
| 30+ | ×2.00 |

**Мягкий сброс** — пропуск одного дня: минус один уровень, не обнуление.

**Anti-gaming:** для зачёта дня страйка требуется хотя бы одно действие с `effort_minutes > 0`. Исключает «токен-коммит в 00:59».

---

## 8. Баллы → Бонусы

```
daily_bonuses_added = min(effective_today, daily_cap_bonuses)
bonus_balance      += daily_bonuses_added
bonus_balance       = min(bonus_balance, per_user_monthly_cap)
```

При оплате:
```
discount_rub = min(bonus_balance × rate, order_amount × 30%)
```

`max_discount_rate = 30%` — стоп-критерий.

---

## 9. Реферальная программа (отдельная статья)

Рефералы финансируются из **referral_budget = revenue × 5%**, не из loyalty_budget.

| Событие | Что получает пилот |
|---|---|
| `referral_registered` | Баллы: base = 1 × rarity(≈15) × G4(4) ≈ **60 баллов** |
| `referral_paid` | Бонусы из referral_budget: `bonus = payment_rub × referral_rate / rate` |

**Пример:** друг оплатил 5 000 ₽. referral_rate=10%, rate=0.05:
```
referral_bonus = 5 000 × 0.10 / 0.05 = 10 000 бонусов
```

---

## 10. Сколько реально получит пользователь

**Ученик МИМ (qual_mult=1.0), страйк 7 дней (×1.2), rarity=1.0:**

| Что делает | Кол-во | effective | Сумма |
|---|:---:|:---:|:---:|
| Урок | 2 | 11.1 | 22.2 |
| Саморазвитие-слот | 2 | 8.2 | 16.4 |
| Помодоро | 2 | 1.2 | 2.4 |
| Git-коммит | 1 | 2.4 | 2.4 |
| Coding (1ч) | 1 | 27.2 | 27.2 |
| Pack update | 1 | 3.6 | 3.6 |
| Комментарий в клубе | 2 | 4.8 | 9.6 |
| **Итого за день** | | | **83.4** |
| **Итого за месяц (30 дн)** | | | **2 502** |

Бонусы: `min(2 502, 200×30) = 2 502`. Скидка: `2 502 × 0.05 = 125 ₽`.

**Мастер (qual_mult=3.0), страйк 30+ дней (×2.0):**

| Что делает | Кол-во | effective | Сумма |
|---|:---:|:---:|:---:|
| WP завершён | 1 | 66.7×3×2 = 400 | 400 |
| Контент опубликован | 1 | 42.2×3×2 = 253 | 253 |
| Знание извлечено | 1 | 40.8×3×2 = 245 | 245 |
| Урок | 2 | 11.1×3×2 = 67 | 134 |
| Coding (1ч) | 1 | 27.2×3×2 = 163 | 163 |
| **Итого за день** | | | **1 195** |
| **Итого за месяц** | | | **35 850** |

Бонусы: `min(35 850, 600×30) = 18 000` (cap truncation). Скидка: `18 000 × 0.05 = 900 ₽`.

---

## 11. Управление параметрами

| Параметр | Где | Как часто | Значение |
|---|---|---|---|
| `rate` | Вычисляется через EMA | 1-е число | Старт: 0.05 |
| `floor` | `loyalty_pool_config` | Редко | 0.01 ₽/бонус |
| `hard_ceiling` | `loyalty_pool_config` | Редко | 0.20 ₽/бонус |
| `K` | `loyalty_pool_config` / env var | По решению | **8** (было 10) |
| `safety_margin` | `loyalty_pool_config` | Ежемесячно | 25% |
| `monthly_loyalty_budget` | `loyalty_pool_config` | Ежемесячно | revenue × 10% |
| `referral_rate` | `loyalty_pool_config` | По решению | 10% от оплаты |
| `per_user_monthly_cap` | `loyalty_pool_config` | По решению | ~3 000 бонусов |
| `effort_minutes` per event_type | `event_impact_matrix` | Редко | См. таблицы §5 |
| `group_mult` per event_type | `event_impact_matrix` | Редко (ArchGate) | G1–G4 |
| `max_per_day` per event_type | `event_impact_matrix` | По решению | Anti-spam |
| `rarity_mult` | Вычисляется | Snapshot 1-го числа | clamp(0.5, 3.0) |

---

## 12. Roadmap

### Приоритет 1 — миграция схемы (~2ч)

- [ ] `ALTER TABLE reference.reward_rules ADD COLUMN effort_minutes INTEGER DEFAULT NULL`
- [ ] `ALTER TABLE reference.reward_rules ADD COLUMN is_marker BOOLEAN DEFAULT FALSE`
- [ ] `ALTER TABLE reference.reward_rules ADD COLUMN max_per_day INTEGER DEFAULT 1`
- [ ] `ALTER TABLE reference.reward_rules ADD COLUMN group_mult INTEGER DEFAULT 1`
- [ ] UPDATE: заполнить по таблицам §5
- [ ] `ALTER TABLE reference.loyalty_pool_config ADD COLUMN K INTEGER DEFAULT 8`
- [ ] `ALTER TABLE reference.loyalty_pool_config ADD COLUMN floor NUMERIC DEFAULT 0.01`
- [ ] `ALTER TABLE reference.loyalty_pool_config ADD COLUMN hard_ceiling NUMERIC DEFAULT 0.20`
- [ ] `ALTER TABLE reference.loyalty_pool_config ADD COLUMN per_user_monthly_cap INTEGER DEFAULT 3000`
- [ ] Функция `compute_rarity_snapshot()` — расчёт rarity раз в месяц
- [ ] Функция `compute_rate_ema()` — пересчёт 1-го числа через EMA(0.3)

### Приоритет 2 — projection-worker v4.2 (~4–6ч)

- [ ] Внедрить `effort_factor` + `rarity_mult` + `group_mult`
- [ ] `daily_total_cap` с K=8 в логике (rolling sum per account_id per day)
- [ ] `per_user_monthly_cap` enforcement
- [ ] `max_per_day` enforcement
- [ ] Clamped rarity [0.5, 3.0] из snapshot-таблицы

### Приоритет 3 — курс и бюджет (~2ч)

- [ ] EMA-функция обновления rate 1-го числа
- [ ] Разделить loyalty_budget и referral_budget в таблицах учёта
- [ ] UI: показать курс и дату пересмотра
- [ ] Реферальный handler `referral_paid`

### Post-MVP (roadmap)

- [ ] `WEEKLY_POOLS_ENABLED` — еженедельные пулы бонусов (против «run on the bank»). Включить после анализа первого месяца: есть ли концентрация активности в начале месяца?

---

## 13. Открытые вопросы для обсуждения

1. **per_user_monthly_cap = 3 000 бонусов** — предварительная оценка. Нужно утвердить: `effective_pool / N × safety_factor`?
2. **K=8 review** — после первого полного месяца реальных данных. Хранить историю K-изменений в таблице.
3. **group_mult G4** при росте N: G4-события умножают base на 4; при большом комьюнити G4-эмиссия может перерасти K=8. Мониторить отдельно.
4. **SDT «причастность»** — мотивационный слой сообщества в v4.2 слабый. Перспектива: групповые challenge с дополнительным group_bonus (вне текущего scope).

---

*Документ подготовлен на основе peer-сессии Claude + Kimi, 27 мая 2026. Session ID: 2026-05-27-14-points-bonus-model-calibration.*
