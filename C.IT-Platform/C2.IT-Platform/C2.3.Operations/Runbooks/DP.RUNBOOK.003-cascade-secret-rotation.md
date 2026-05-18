---
id: DP.RUNBOOK.003
name: "Runbook: Cascade Secret Rotation"
type: domain-entity
status: active
summary: "Процедура ротации одного секрета по N точкам хранения с матрицей зависимостей. Триггер: perceived breach или плановая ротация по B2.3."
created: 2026-04-28
wp: WP-212
trust:
  F: 4
  G: domain
  R: 0.7
epistemic_stage: validated
related:
  - id: DP.RUNBOOK.001
    type: complements
  - id: WP-212
    type: realizes
---

# Runbook: Cascade Secret Rotation

> **Когда дочитать до конца:** ты держишь в руках один секрет и нужно прокрутить его через N систем-потребителей без simultanéous downtime. Источник истины процедуры — этот документ; источник истории — `B2.1-secrets-inventory.md`; источник расписания — `B2.3-rotation-policy.md`.

---

## 1. Когда применять

| Триггер | Срочность | Класс события |
|---------|-----------|---------------|
| **Perceived breach** (показ в чате/логе/коммите/screenshot/voice) | Немедленно (в текущей сессии) | Инцидент → post-mortem обязателен |
| **Известный compromise** (audit log показал unauthorized access) | Немедленно (≤1h) | Инцидент → post-mortem обязателен |
| **Плановая** по календарю B2.3 | По расписанию | Routine |
| **Смена доступа** члена команды (увольнение, перевод, окончание контракта) | До конца рабочего дня | Routine |
| **Подозрение** (необъяснимая активность, alerts) | ≤24h после triage | Инцидент → расследование |

**Если триггер perceived breach** — первое действие до запуска runbook: записать инцидент в `Incidents/YYYY-MM-DD-secret-leak.md` (хотя бы 3 строки: что, когда, через какой канал). Без этого нечего разбирать на post-mortem'е.

---

## 2. Pre-flight checks (5-10 мин)

### 2.1. Определить класс секрета

| Класс | Примеры | Cascade-сложность |
|-------|---------|-------------------|
| **Database URL** (`DATABASE_URL`, `NEON_*_URL`) | Neon credentials, Railway PG | Высокая (10-15 точек) |
| **OAuth provider secret** (Ory, GitHub, Google) | `ORY_CLIENT_SECRET`, `GITHUB_CLIENT_SECRET` | Средняя (3-5 точек) |
| **API key платформенный** (Anthropic, OpenAI, Linear, Railway, CF) | `ANTHROPIC_API_KEY`, `LINEAR_API_KEY` | Низкая (1-3 точки) |
| **Webhook secret** (HMAC, signature) | `GITHUB_WEBHOOK_SECRET`, `YOOKASSA_HMAC` | Низкая-средняя (1-2 точки + provider config) |
| **Bot token** (Telegram) | `TELEGRAM_BOT_TOKEN` | Низкая (1-2 точки) |
| **Service-account password** | Aisystant `tech@`, internal service users | Низкая (1-3 точки) |

### 2.2. Собрать карту точек хранения

Источник: `B2.1-secrets-inventory.md` + grep по репо. Шаблон:

```bash
# Для секрета SECRET_NAME — найти все упоминания
cd ~/IWE
grep -rn "SECRET_NAME" --include="*.toml" --include="*.yml" --include="*.yaml" \
  --include="wrangler.toml" --include="*.env*" 2>/dev/null
grep -rn "SECRET_NAME" .secrets/ 2>/dev/null
# Cloudflare Workers
for w in DS-MCP/*/; do
  if [ -f "$w/wrangler.toml" ]; then
    cd "$w" && wrangler secret list 2>/dev/null | grep SECRET_NAME && cd -
  fi
done
# Railway
railway variables -e production 2>/dev/null | grep SECRET_NAME
```

Если секрет ≥ 5 точек — построить чек-лист в TodoWrite (по точке = задача).

### 2.3. Идентифицировать «источник» и «потребителей»

- **Источник** = система, где секрет создаётся/выдаётся (Neon console для DB URL, Ory admin для client_secret, провайдер для API key).
- **Потребители** = системы, которые используют секрет (CF Worker'ы, Railway services, local scripts, .secrets/ файлы).

Cascade order: **сначала создать новый**, потом обновить потребителей, последним — revoke старый. Не наоборот.

### 2.4. Оценить blast radius

| Если потребитель упадёт во время rotation | Severity | Действие |
|-------------------------------------------|----------|----------|
| Бот @aist_me_bot (prod канал) | критическая | Делать в окно низкой нагрузки (ночь МСК), готовить fallback |
| Gateway/MCP-сервисы | высокая | Делать с graceful update, не во время Strategy Session |
| Activity-hub / projection-worker | средняя | OK в рабочее время |
| Local scripts / .secrets/ | низкая | OK в любое время |
| Аналитика (Metabase, Langfuse) | низкая | OK в любое время |

---

## 3. Процедура (cascade)

### Шаг 0: Создать новый секрет (источник)

Не revoke старый сразу. Сначала создать новый в источнике; старый и новый коротко сосуществуют.

| Источник | Команда / процедура |
|----------|---------------------|
| Neon | console.neon.tech → Settings → Reset password (или Branch credentials) — получить новый URL |
| Cloudflare API | dash.cloudflare.com → My Profile → API Tokens → Create Token (с тем же scope, что старый) |
| Ory | `ory patch oauth2-client <client_id>` или dashboard → создать новый secret рядом со старым |
| GitHub OAuth App | github.com/settings/developers → app → Generate new client secret |
| **GitHub App (private key)** | `github.com/organizations/<org>/settings/apps/<app-slug>` → **Private keys** → **Generate a private key** → скачать `.pem`. ⚠️ Если app зарегистрирован на **личном** аккаунте — URL: `github.com/settings/apps/<app-slug>`. Для org `aisystant` и app `aisystant-knowledge`: `https://github.com/organizations/aisystant/settings/apps/aisystant-knowledge` |
| Google OAuth | console.cloud.google.com → APIs → Credentials → Create new key |
| Anthropic / OpenAI | console.anthropic.com / platform.openai.com → API keys → Create new |
| Telegram bot | @BotFather → /token → /revoke — **исключение:** Telegram не поддерживает coexistence, новый сразу заменяет старый. Готовь бот к downtime ~5 мин. |

**Записать** новый секрет в `~/IWE/.secrets/<service>-<purpose>` (chmod 600). Не передавать в чат/логи (см. правило 25 в `feedback_behaviour.md`).

### Шаг 1: Обновить потребителей в порядке от наименее критичных к наиболее критичным

Логика: если что-то сломается на ранних шагах, prod ещё работает на старом секрете. Откат проще.

**Канонический порядок:**

1. **Local scripts + `.secrets/`** (~/IWE/.secrets/<key>) — обновить файл, проверить wrapper-скриптом.
2. **Аналитика и наблюдаемость** (Langfuse, Metabase, observability-webhook, status-proxy) — обновить env, перезапустить если нужно.
3. **Worker-сервисы вторичные** (multi-domain-projection-worker, bridge-2-events-poller, payment-registry) — `wrangler secret put` или Railway env. ⚠️ `rewards-projection-worker` decommission'd 2026-05-17 (WP-311 Ф-Close), функционал поглощён multi-domain.
4. **MCP-бэкенды** (knowledge-mcp, digital-twin-mcp, personal-knowledge-mcp, event-gateway, payment-receiver) — `wrangler secret put` + smoke.
5. **Gateway-MCP** (gateway-mcp) — обновить, перепроверить routing к бэкендам.
6. **Activity-hub** (Railway) — `railway variables --set`, перезапустить.
7. **Бот** (@aist_me_bot prod, @aist_pilot_me) — обновить Railway env, **последний** в каскаде. Pilot первым (Pilot-First правило), prod последним.
8. **Neon-migrations** (local + GHA) — обновить если использует rotated DB URL.

**Команды по типу хранения:**

```bash
# Cloudflare Worker
cd ~/IWE/DS-MCP/<service>
echo "$NEW_VALUE" | wrangler secret put SECRET_NAME --env production

# Railway
cd <service>
railway variables --set "SECRET_NAME=$NEW_VALUE" -e production

# GitHub Actions (если секрет используется в CI)
gh secret set SECRET_NAME -b "$NEW_VALUE" --repo <org>/<repo>

# Local .secrets/
echo "$NEW_VALUE" > ~/IWE/.secrets/<service>-<purpose>
chmod 600 ~/IWE/.secrets/<service>-<purpose>
```

### Шаг 2: Smoke-test после каждой точки

Не двигаться дальше пока текущая точка не подтверждена. Канонические smoke:

| Точка | Smoke-команда |
|-------|---------------|
| CF Worker (gateway-mcp / knowledge-mcp / etc) | `curl -fsS https://<worker>.<acc>.workers.dev/health` или специфичный endpoint |
| Railway service (бот, activity-hub) | `railway logs` 30 сек, ищем «started» / отсутствие `auth failed` / `connection refused` |
| MCP-бэкенд через Gateway | `claude mcp call <tool> --args '{"q":"test"}'` (если есть) или ручной запрос с JWT |
| Бот | отправить `/start` второму аккаунту (не основному); проверить `/link` если затронуты Ory tokens |
| Neon-migrations | `cd neon-migrations && python apply.py --dry-run` |

**Если smoke FAIL** — откатить шаг (старое значение ещё работает в источнике), исследовать, не двигаться вперёд.

### Шаг 3: Revoke старого секрета (источник)

Только когда **все** потребители обновлены и smoke PASS. Логика: после revoke старый ключ перестанет работать — точка возврата закрыта.

| Источник | Команда |
|----------|---------|
| Neon | console.neon.tech → старый branch/role → Drop / Reset |
| Cloudflare API | dash.cloudflare.com → API Tokens → Roll / Delete старый |
| Ory | `ory delete oauth2-client-secret <id>` или dashboard → Revoke старый |
| GitHub / Google OAuth | dashboard → revoke старый client secret |
| **GitHub App private key** | org settings → Private keys → **Delete** старый ключ (он помечен датой генерации) |
| Anthropic / OpenAI | dashboard → API keys → Revoke старый |
| Telegram | (выполнен на шаге 0, особый случай) |

### Шаг 4: Финальная верификация

```bash
# Проверка 1: старый секрет действительно не работает
# (попробовать с старым значением — должен быть 401/403)

# Проверка 2: новые секреты применились везде — пройти по списку с шага 1
for service in <list>; do curl -fsS <health-endpoint> ; done

# Проверка 3: production-сценарий end-to-end
# Бот: /start, /link, поиск через knowledge-mcp, обращение к dt-mcp
```

---

## 4. Post-rotation

### 4.1. Журнал

Запись в `B2.3-rotation-policy.md` § Журнал ротаций:
```
| YYYY-MM-DD | <SECRET_NAME> | <триггер> | <время на cascade> | <инциденты> |
```

### 4.2. Обновить календарь B2.3

Сместить «Следующая ротация» на 90/180/365 дней вперёд от текущей даты (по классу из B2.3 §Расписание).

### 4.3. Если триггер был breach — post-mortem

Записать в `Incidents/YYYY-MM-DD-secret-leak.md`:
- Что просочилось (тип секрета, не значение).
- Канал утечки (git / chat / log / screenshot / voice).
- Time-to-detect (когда узнали).
- Time-to-rotate (когда закрыли).
- Затронутые точки (число + список).
- Что предотвратило бы повтор: pre-commit hook, output-фильтр, дисциплина, audit log алерт?

Связать инцидент с `feedback_behaviour.md` Правило 25 — если паттерн новый, расширить правило.

### 4.4. Если cascade > 1h — ретроспектива процесса

Что замедлило?
- Не было map зависимостей (тогда добавить в B2.1)?
- Не было wrapper-скриптов (тогда писать)?
- Smoke-тесты ручные вместо автоматических (тогда автоматизировать)?
- Slack/TG-координация с Димой/Пашей задерживала (тогда runbook предполагать самостоятельность)?

---

## 5. Карта высокочастотных секретов (короткая)

> Полная — в `B2.1-secrets-inventory.md`. Здесь — топ-10 для быстрого подъёма.

| Секрет | Класс | Точки хранения (порядок cascade) |
|--------|-------|----------------------------------|
| `DATABASE_URL` (Neon main) | DB URL | .secrets/, neon-migrations (local), 6 CF Workers (DS-MCP/*), 4 Railway services, GHA |
| `ORY_CLIENT_SECRET` | OAuth secret | gateway-mcp, knowledge-mcp, digital-twin-mcp, personal-knowledge-mcp |
| `TELEGRAM_BOT_TOKEN` | Bot token | bot Railway (pilot + prod), .secrets/ |
| `ANTHROPIC_API_KEY` | API key | bot Railway, claude-code config (local) |
| `GITHUB_APP_PRIVATE_KEY` | Service key | knowledge-mcp (для personal repo OAuth flow) |
| `LINEAR_API_KEY` | API key | .secrets/mcp-linear.sh |
| `RAILWAY_API_TOKEN` | API key | .secrets/mcp-railway.sh |
| `CLOUDFLARE_API_TOKEN` | API key | .secrets/, GHA для деплоя CF Workers |
| `OPENAI_API_KEY` | API key | knowledge-mcp (embeddings) |
| `YOOKASSA_*` (HMAC + secret_key) | Webhook + API | payment-receiver, payment-registry |

---

## 6. Прецеденты

- **2026-04-27** (инцидент cascade leak, WP-253 Ф11.19): сырые пароли утекли в Claude chat → cascade rotation 14 точек хранения за ~1.5h. Канал утечки: AI chat. Урок: правило 25 в `feedback_behaviour.md` (от 25 апр) сработало реактивно (post-leak rotation), но не предотвратило повторного события через 2 дня → правило усилено превентивным разделом 28 апр; этот runbook создан как рабочий инструмент cascade.

---

## 7. Связи

- `B2.1-secrets-inventory.md` — карта секретов и точек хранения.
- `B2.3-rotation-policy.md` — расписание плановой ротации.
- `feedback_behaviour.md` Правило 25 — превентивная сторона (не показывать секреты в чате).
- `WP-212` Ф2 + B2.6 — задача-владелец этого runbook.
- `Incidents/` — журнал инцидентов утечек.
