# WP-285: Инфраструктура платформы — полное сравнение

> **Документ для встречи 14.** Два варианта мировой платформы (Track B) + российская платформа (Track A) в конце.

---

## Мировая платформа (Track B)

### Что входит в мировую платформу

| Слой | Что нужно |
|------|-----------|
| **Compute** | Запуск бота, projection workers |
| **Аутентификация** | Ory EU (Kratos + Hydra) — мировые пользователи |
| **База данных** | Postgres для entity БД + отдельная БД для Ory |
| **API-слой** | CF Workers — gateway-mcp, knowledge-mcp, event-gateway |
| **DNS / SSL** | Cloudflare — мировой домен |
| **Мониторинг** | Better Stack — keyword-check мониторы |
| **Платежи** | Stripe |

---

### Вариант 1 — Vultr (EU)

> Андрей знает платформу. Самый дешёвый старт. Ручное управление серверами.

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **Vultr VPS 2GB** (Amsterdam / Frankfurt) | Ory EU: Kratos + Hydra + Postgres-for-Ory | $12 |
| **Vultr VPS 4GB** (Amsterdam / Frankfurt) | Мировой бот + Projection workers | $20 |
| **Vultr Managed Postgres** (EU) | Entity БД: platform, events, knowledge, payments, health | $15 |
| **CF Workers** | gateway-mcp (world), knowledge-mcp, event-gateway | $5 |
| **Cloudflare** | DNS + SSL (aisystant.com) | $0–10 |
| **Better Stack** | Мониторы мировых сервисов | $10 |
| **Stripe** | Приём оплаты | 2.9% + $0.30 |
| **ИТОГО MVP** | | **~$62–72/мес** |

**Production (1–5K пользователей):**
+$40 (2 VPS для масштабирования) + $15 (рост БД) + $10 (мониторы) = **~$127–137/мес**

**Управление:** Docker Compose на старте → k3s при росте >2K пользователей.
Миграция при росте: ~40h.
**Egress:** $0.01/GB — при 100GB/мес = $1.
**DevOps:** Андрей.

---

### Вариант 2 — GKE Autopilot (EU) ← рекомендуется

> Google Managed Kubernetes. Плата только за реально потреблённые ресурсы pods — idle не тарифицируется.
> SOC2 / GDPR attestation — важно для YC и корпоративных клиентов.

#### ⭐ Бесплатные первые 3 месяца

Google предоставляет $300 кредита на 90 дней при первой регистрации GCP аккаунта.
При MVP стоимости ~$91–131/мес кредита хватает практически на весь первый квартал — платформа запускается за $0.

Кто активирует: нужен новый Google аккаунт или аккаунт без истории GCP. Активировать до запуска кластера.

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **GKE Autopilot** (europe-west4, Нидерланды) | K8s кластер. Pods: Ory Kratos + Ory Hydra + Мировой бот + Projection workers. Автомасштабирование встроено | $60–80 |
| **Cloud SQL Postgres** (europe-west4) | Managed Postgres для всех entity БД + Ory. Один инстанс, несколько databases | $15–25 |
| **Artifact Registry** (GCP, EU) | Docker-образы: Ory, бот, workers | $0.5 |
| **CF Workers** | gateway-mcp (world), knowledge-mcp, event-gateway | $5 |
| **Cloudflare** | DNS + SSL (aisystant.com) | $0–10 |
| **Better Stack** | Мониторы мировых сервисов | $10 |
| **Stripe** | Приём оплаты | 2.9% + $0.30 |
| **ИТОГО MVP** | **первые 3 мес: ~$0 (кредит)** | **далее: ~$91–131/мес** |

**Production (1–5K пользователей):**
Pods масштабируются автоматически (+$80–120) + Cloud SQL small (+$70) = **~$241–321/мес**

**Управление:** kubectl + Helm. CI/CD через GitHub Actions → Cloud Build. Масштабирование автоматическое.
**Egress:** $0.12/GB исходящий. Трафик GKE ↔ Cloud SQL в том же регионе = $0.
**DevOps:** Паша (обучение ~4–6h по kubectl / Helm).

---

### Сравнение двух вариантов

| | Vultr | GKE Autopilot |
|--|-------|----------------|
| **MVP стоимость** | ~$62–72/мес | ~$0 первые 3 мес, далее ~$91–131/мес |
| **Production** | ~$127–137/мес | ~$241–321/мес |
| **Масштабирование** | Ручное (добавлять VPS) | Автоматическое ✅ |
| **Миграция при росте** | Нужна (~40h) | Не нужна ✅ |
| **SOC2 / GDPR** | ❌ | ✅ Google |
| **Egress** | $0.01/GB | $0.12/GB |
| **Free tier** | Нет | $300 / 90 дней ✅ |
| **DevOps owner** | Андрей | Паша |

---

### Открытые вопросы для встречи 14

| # | Вопрос | Влияет на |
|---|--------|-----------|
| О-3 | Паша: готов к GKE (обучение kubectl / Helm)? | Выбор варианта |
| О-4 | Андрей: что уже на текущем Vultr? Новый EU-аккаунт или существующий? | Вариант 1 |
| О-5 | Vultr Managed Postgres или Neon EU (Amsterdam) для entity БД? | Вариант 1 |
| О-9 | GCP Free Tier ($300): у кого нет истории GCP — кто активирует? | Вариант 2 |
| О-8 | Юрлицо для Stripe: UK / US LLC / Кипр? | Оба варианта, Ф4 |
| О-6 | Основной домен: aisystant.com или новый? | Оба варианта, Ф5 |

---

---

## Российская платформа (Track A)

> Отдельная инфраструктура для российских пользователей. Передаётся Ильшату (WP-281).
> Переход на VK Cloud Kubernetes — замена Railway как compute-платформы.

### Полный стек Track A

| Компонент | Что делает | Стоимость/мес |
|-----------|-----------|---------------|
| **VK Cloud Kubernetes** | Managed K8s для RU: бот @aist_me_bot + projection workers (заменяет Railway) | ~₽4 000–8 000 (~$44–88) |
| **Neon (12 БД)** | Все entity БД российской платформы: platform, events, knowledge, payments, health, content, digital-twin, activity-hub, personas, learning, guides, ory | $69 |
| **VK Cloud Ory** | Kratos + Hydra — аутентификация российских пользователей | ~$10–20 |
| **CF Workers** | gateway-mcp (RU), knowledge-mcp, event-gateway, payment-receiver, guides-mcp, digital-twin-mcp | $5 |
| **Cloudflare** | DNS + SSL (aisystant.ru, mcp.aisystant.com) | $0–10 |
| **Better Stack** | Мониторинг RU-сервисов | $10 |
| **YooKassa** | Приём оплаты от российских пользователей | ~3.5% транзакции |
| **Hetzner tsekh-1** | Dedicated сервер Тсерена (NixOS + ZFS) — CD pipeline, резерв | €44 (~$48) |
| **ИТОГО Track A** | | **~$186–260/мес** |

> **Статус VK Cloud K8s:** нужно уточнить тариф (количество worker-нод, регион). Текущая оценка — минимальный кластер 2 worker-ноды 2vCPU/4GB.

### Переход Railway → VK Cloud Kubernetes

| Было (Railway) | Станет (VK Cloud K8s) |
|----------------|----------------------|
| Deployment-сервис Python-бота | K8s Deployment |
| Railway workers | K8s Job / CronJob |
| Railway env vars | K8s Secrets / ConfigMap |
| Railway logs | VK Cloud Logging или stdout |
| Railway auto-deploy из GitHub | GitHub Actions → kubectl apply |

**Ответственный:** Ильшат (после передачи WP-281) + Андрей (помощь при настройке).
