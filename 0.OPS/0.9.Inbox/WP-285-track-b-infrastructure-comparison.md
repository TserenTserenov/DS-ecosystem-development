# WP-285: Мировая платформа (Track B) — два варианта стека

> **Документ для встречи 14.** Полный состав инфраструктуры для мировой платформы.
> Два варианта: Vultr EU vs GKE Autopilot EU.

---

## Что входит в мировую платформу

| Слой | Что нужно |
|------|-----------|
| **Compute** | Запуск бота, projection workers |
| **Аутентификация** | Ory EU (Kratos + Hydra) — мировые пользователи |
| **База данных** | Postgres для entity БД (events, knowledge, payments, platform, ...) + отдельная БД для Ory |
| **API-слой** | CF Workers — gateway-mcp, knowledge-mcp, event-gateway |
| **DNS / SSL** | Cloudflare — мировой домен |
| **Мониторинг** | Better Stack — keyword-check мониторы |
| **Платежи** | Stripe |
| **Репозиторий образов** | Хранение Docker-образов (только GKE) |

---

## Вариант 1 — Vultr (EU)

> Андрей знает платформу. Дешевле всего на старте. Ручное управление серверами.

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **Vultr VPS 2GB** (Amsterdam / Frankfurt) | Ory EU: Kratos + Hydra + Postgres-for-Ory | $12 |
| **Vultr VPS 4GB** (Amsterdam / Frankfurt) | Мировой бот (@bot) + Projection workers | $20 |
| **Vultr Managed Postgres** (EU) | Entity БД мировой платформы: platform, events, knowledge, payments, health (5 БД на старте) | $15 |
| **CF Workers** | gateway-mcp (world), knowledge-mcp, event-gateway | $5 |
| **Cloudflare** | DNS + SSL (aisystant.com) | $0–10 |
| **Better Stack** | Мониторы мировых сервисов | $10 |
| **Stripe** | Приём оплаты | 2.9% + $0.30 |
| **ИТОГО MVP** | | **~$62–72/мес** |

**Production (1–5K пользователей):**

| Добавляется | Стоимость |
|-------------|-----------|
| +2 Vultr VPS 4GB (масштабирование workers) | +$40 |
| Vultr Managed Postgres (рост данных) | +$15 |
| Better Stack (доп. мониторы) | +$10 |
| **ИТОГО Production** | **~$127–137/мес** |

**Управление:** Docker Compose на старте → k3s или Docker Swarm при росте >2K пользователей.
**Egress:** $0.01/GB — при 100GB/мес = $1 (незначительно).
**Ответственный:** Андрей (DevOps).

---

## Вариант 2 — GKE Autopilot (EU)

> Google managed Kubernetes. Плата только за реально потреблённые ресурсы pods — без оплаты idle.
> SOC2 / GDPR attestation — важно для YC.
> **$300 кредит / 90 дней** через GCP Free Tier → MVP первые 3 месяца практически бесплатно.

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **GKE Autopilot** (europe-west4, Нидерланды) | K8s кластер. Pods: Ory Kratos + Ory Hydra + Мировой бот + Projection workers. Автомасштабирование встроено | $60–80 |
| **Cloud SQL Postgres** (europe-west4) | Managed Postgres для всех entity БД + Ory БД. Один инстанс, несколько databases | $15–25 |
| **Artifact Registry** (GCP, EU) | Docker-образы: Ory, бот, workers | $0.5 |
| **CF Workers** | gateway-mcp (world), knowledge-mcp, event-gateway | $5 |
| **Cloudflare** | DNS + SSL (aisystant.com) | $0–10 |
| **Better Stack** | Мониторы мировых сервисов | $10 |
| **Stripe** | Приём оплаты | 2.9% + $0.30 |
| **ИТОГО MVP** | | **~$91–131/мес** |

**Production (1–5K пользователей):**

| Что происходит | Стоимость |
|----------------|-----------|
| GKE pods автоматически масштабируются | +$80–120 |
| Cloud SQL → small instance (2 vCPU, 50GB) | +$70 |
| **ИТОГО Production** | **~$241–321/мес** |

**Управление:** kubectl + Helm. CI/CD через GitHub Actions → Google Cloud Build.
**Egress предупреждение:** $0.12/GB исходящего трафика из GKE. Трафик GKE ↔ Cloud SQL в том же регионе = $0.
**Ответственный:** Паша (обучение ~4–6h по kubectl / Helm).

---

## Сравнение двух вариантов

| | Vultr | GKE Autopilot |
|--|-------|----------------|
| **MVP стоимость** | ~$62–72/мес | ~$91–131/мес |
| **Production стоимость** | ~$127–137/мес | ~$241–321/мес |
| **Старт** | Docker Compose (быстро) | kubectl + Helm (~4–6h обучения) |
| **Масштабирование** | Ручное (добавлять VPS) | Автоматическое ✅ |
| **Миграция при росте** | Нужна (~40h) | Не нужна ✅ |
| **SOC2 / GDPR** | ❌ | ✅ Google |
| **Egress** | $0.01/GB | $0.12/GB |
| **Free tier** | Нет | $300 / 90 дней ✅ |
| **DevOps owner** | Андрей | Паша |

---

## Открытые вопросы для встречи 14

| # | Вопрос | Влияет на |
|---|--------|-----------|
| О-3 | Паша: готов к GKE (обучение kubectl / Helm)? | Выбор варианта |
| О-4 | Андрей: что уже на текущем Vultr? Новый EU-аккаунт или использовать существующий? | Вариант 1 |
| О-5 | Vultr Managed Postgres или Neon EU (Amsterdam) для entity БД? | Вариант 1 |
| О-9 | GCP Free Tier ($300): кто активирует аккаунт? | Вариант 2 |
| О-8 | Юрлицо для Stripe: UK / US LLC / Кипр? | Оба варианта, Ф4 |
| О-6 | Основной домен: aisystant.com или новый? | Оба варианта, Ф5 |
