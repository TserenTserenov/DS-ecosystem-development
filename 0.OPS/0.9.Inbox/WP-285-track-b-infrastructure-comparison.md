# WP-285: Три варианта полного стека — сравнение

> **Документ для встречи 14.** Что именно входит в платформу при каждом варианте, и сколько всё это стоит.
> Связан с: WP-285, WP-73, WP-253

---

## Что сравниваем

Три полных стека мировой платформы (Track B). Каждый вариант — **полный список всего**, что нужно, чтобы платформа работала: вычисления, БД, аутентификация, API, мониторинг, платежи.

| Слой | Вариант 1 (текущий) | Вариант 2 (Vultr) | Вариант 3 (GKE Autopilot) |
|------|---------------------|-------------------|---------------------------|
| **Compute** | Hetzner tsekh-1 + Railway | Vultr VPS (EU) | GKE Autopilot (EU) |
| **База данных** | Neon (12 БД, DBaaS) | Vultr Managed Postgres | Cloud SQL (Google) |
| **Аутентификация** | VK Cloud Ory (RU) | Ory EU на Vultr VPS | Ory EU в GKE pod |
| **API-слой** | CF Workers | CF Workers (те же) | CF Workers (те же) |
| **DNS / SSL** | Cloudflare | Cloudflare (тот же) | Cloudflare (тот же) |
| **Мониторинг** | Better Stack | Better Stack (тот же) | Better Stack (тот же) |
| **Платежи** | YooKassa | Stripe | Stripe |

> CF Workers, Cloudflare, Better Stack не меняются ни в одном варианте — платим один раз, используем для всех платформ.

---

## Вариант 1 — Текущий стек (Track A / Россия)

> Справочно: что работает сейчас. При запуске Track B этот стек остаётся для российских пользователей (Track A → Ильшат).

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **Hetzner tsekh-1** | Dedicated сервер (NixOS + ZFS mirror), резервный Mac, deploy-rs CD | €44 (~$48) |
| **Railway** | Python-бот @aist_me_bot + projection workers (2 сервиса) | $20–35 |
| **Neon — 12 БД** | platform-core, events (~10GB append), knowledge (~5GB+pgvector), payments, health (~1GB), content, digital-twin, activity-hub, ory-internal, personas, learning, guides | $69 |
| **CF Workers (Paid)** | gateway-mcp, knowledge-mcp, event-gateway, payment-receiver, guides-mcp, digital-twin-mcp | $5 |
| **Cloudflare** | DNS + SSL (mcp.aisystant.com, aisystant.ru) + WAF | $0–20 |
| **VK Cloud Ory** | Kratos (регистрация/логин) + Hydra (OAuth2/JWT) — только российские пользователи | $10–20 |
| **Better Stack** | Мониторинг 9 сервисов (keyword-check, см. HD #51) | $0–10 |
| **YooKassa** | Приём оплаты от российских пользователей | ~3.5% транзакции |
| **Telegram Bot API** | Канал связи с пользователями | $0 |
| **ИТОГО** | | **~$152–207/мес** |

---

## Вариант 2 — Vultr (EU)

> Andrey знает платформу. Дешевле GKE, дороже Hetzner Cloud.
> Р-6 принято: Ory EU на Vultr независимо от остального выбора.

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **Vultr VPS 2GB (Amsterdam)** | Ory EU: Kratos + Hydra + Postgres-for-Ory | $12 |
| **Vultr VPS 4GB (Amsterdam)** | World bot (@aisystant_world_bot) + projection workers | $20 |
| **Vultr Managed Postgres (EU)** | Track B entity БД: platform-b, events-b, knowledge-b, payments-b, ory-b (5 БД для старта) | $15 |
| **CF Workers** | gateway-mcp (world endpoint) + knowledge-mcp + event-gateway | $0 (тот же $5 план) |
| **Cloudflare** | DNS + SSL (aisystant.com или новый домен) | $0 (тот же аккаунт) |
| **Better Stack** | World monitors (новые) | $0 (в текущем плане) |
| **Stripe** | Оплата от нероссийских пользователей | 2.9% + $0.30 |
| **Telegram Bot API** | $0 | $0 |
| **ИТОГО Track B** | | **~$47/мес** |

**Итого (Track A + Track B на Vultr):** ~$199–254/мес

**Управление:** Docker Compose на старте, k3s при росте >1K пользователей. Миграция ~40h.
**Egress:** $0.01/GB — при 100GB/мес = $1 (незначительно на MVP).

---

## Вариант 3 — GKE Autopilot (EU)

> Managed Kubernetes: плата только за реально потреблённые ресурсы pods (не за idle nodes).
> Tseren предпочитает — «не переделывать при росте».
> **$300 кредит / 90 дней** через GCP Free Tier → MVP фактически бесплатный первые 3 месяца.

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **GKE Autopilot** (europe-west4, Нидерланды) | K8s кластер: pods автоматически. Внутри: Ory Kratos pod + Ory Hydra pod + World bot pod + Projection workers pod | $60–80 |
| **Cloud SQL** (europe-west4) | Managed Postgres для Track B entity БД + отдельная БД для Ory EU. Shared core (f1-micro) на старте | $15–25 |
| **Artifact Registry** (GCP) | Хранение Docker-образов (Ory, бот, workers) | $0.5 |
| **CF Workers** | gateway-mcp (world) + knowledge-mcp + event-gateway | $0 (тот же $5 план) |
| **Cloudflare** | DNS + SSL (aisystant.com) | $0 (тот же аккаунт) |
| **Better Stack** | World monitors | $0 (в текущем плане) |
| **Stripe** | Оплата от нероссийских пользователей | 2.9% + $0.30 |
| **Telegram Bot API** | $0 | $0 |
| **ИТОГО Track B** | | **~$76–106/мес** |

**Итого (Track A + Track B на GKE):** ~$228–313/мес

**Управление:** kubectl + Helm. Автомасштабирование встроено. Паше нужно обучение (~4–6h).
**Egress предупреждение:** $0.12/GB исходящего трафика из GKE. При 100GB/мес = $12. Трафик внутри региона (GKE ↔ Cloud SQL) = $0.

---

## Сравнение при росте

| | Вариант 1 (сейчас) | Вариант 2 (Vultr) | Вариант 3 (GKE) |
|--|-------------------|--------------------|-----------------|
| **MVP** (0–500 пользователей) | $152–207 | +$47 | +$76–106 |
| **Production** (1–5K) | — | +$98 | +$252–297 |
| **Scale** (10K+) | — | +$250–400 | +$600–800 |
| **Миграция при росте** | — | Нужна (~40h) | Не нужна ✅ |
| **SOC2/GDPR attestation** | ❌ | ❌ | ✅ Google |
| **Egress** | 20TB free (Neon включает) | $0.01/GB | $0.12/GB ⚠️ |

---

## Ключевые архитектурные факты

1. **CF Workers не меняются ни в одном варианте** — они stateless, работают на Cloudflare anycast. Просто меняется URL backend'а куда Workers проксируют (Vultr IP или GKE Ingress IP).

2. **Neon (12 БД) остаётся для Track A** при всех вариантах — это данные российских пользователей. Track B начинает с чистых БД (Vultr Managed Postgres или Cloud SQL).

3. **Ory EU = новый инстанс** в обоих вариантах. VK Cloud Ory остаётся для Track A. Это Р-6.

4. **Hetzner tsekh-1** (dedicated) — физический сервер Тсерена. Остаётся при любом варианте (CI/CD, Mac backup). В расходы Track B не входит.

---

## Открытые вопросы для встречи 14

| # | Вопрос | Влияет |
|---|--------|--------|
| О-3 | Паша: готов к зарубежной инфраструктуре? | Вариант 2 или 3 |
| О-4 | Андрей: что уже на текущем Vultr? Использовать или новый аккаунт? | Вариант 2 |
| О-5 | Vultr Managed Postgres или Neon EU (amsterdam) для Track B БД? | Вариант 2 |
| О-9 | GCP Free Tier ($300): кто активирует аккаунт? | Вариант 3 |
| О-10 | Паша обучается GKE за W19-W20 или нужен Андрей как DevOps? | Вариант 3 |
