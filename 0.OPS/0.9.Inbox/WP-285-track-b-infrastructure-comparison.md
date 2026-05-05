---
type: architectural-comparison
title: "Track B инфраструктура — сравнение Hetzner / Vultr / GKE / EKS"
status: draft-for-discussion
created: 2026-05-05
related: WP-285, WP-215, WP-73 (встреча 13)
audience: Андрей (архитектор), Паша (инженер), Тсерен
---

# Track B инфраструктура — сравнение вариантов

> **Контекст:** Встреча 13 (5 мая) приняла Р-TrackB-5 (Vultr) как стартовое решение. Тсерен склоняется к **сразу облако**, чтобы не переделывать при росте. Документ — расчёты для финального выбора.

---

## 1. Требования к инфраструктуре

### Что должно работать в Track B

| Компонент | Назначение | Где сейчас (Track A) | Где должно быть в Track B |
|-----------|------------|---------------------|---------------------------|
| **Ory Kratos + Hydra** | Аутентификация + OAuth/JWT | VK Cloud (RU) | Track B EU |
| **Postgres (12 БД)** | platform, learning, persona, indicators, subscription, finance, security, health, knowledge, content, … | Neon (регион?) | Track B EU (managed или self-hosted) |
| **MCP-сервисы** | gateway, knowledge, event-gateway, payment-receiver, personal-knowledge, guides, digital-twin | CF Workers | **CF Workers (без изменений)** — edge, не зависят от региона |
| **Bot** | aist_bot (aiogram) | Railway | Track B compute |
| **Workers** | multi-domain-projection, rewards-projection, alerter | Railway | Track B compute |
| **Storage** | бэкапы, артефакты | Railway/Neon backups | Track B S3-compatible |
| **DNS/SSL/WAF** | edge-уровень | Cloudflare | Cloudflare (без изменений) |
| **Monitoring** | uptime, alerts | Better Stack | Better Stack (без изменений) |

### Базовая нагрузка

| Сценарий | Активных пользователей | vCPU суммарно | RAM суммарно | Storage |
|----------|------------------------|---------------|--------------|---------|
| **MVP (Q3 2026)** | до 100 | ~5 | ~10 GB | ~100 GB |
| **Production (Q4 2026)** | 100–1000 | ~10 | ~25 GB | ~300 GB |
| **Масштаб (2027)** | 1000–10000 | 30+ | 80+ GB | 1+ TB |

---

## 2. Сравнение трёх вариантов

> Все цены в USD/мес. EUR конвертировано по курсу 1.08. Без учёта egress/traffic (см. §4).

### Вариант A — Hetzner Cloud (EU)

**Регионы:** Falkenstein, Nuremberg, Helsinki — все EU, GDPR из коробки.

| Этап | Конфигурация | Цена |
|------|--------------|------|
| **MVP** | CX32 (4vCPU/8GB/80GB SSD) для Postgres+Ory + CX22 (2vCPU/4GB) для bot/workers + Storage Box BX11 1TB | $13 + $7 + $4 = **$24** |
| **Production** | CX42 (8vCPU/16GB) Postgres + CX32 Ory(2 replicas) + CX22 bot+workers + Storage Box BX21 5TB | $28 + $14 + $7 + $13 = **$62** |
| **Масштаб** | AX41 dedicated (6c Ryzen/64GB/2×512GB NVMe) Postgres + 3×CX32 + Storage Box BX31 10TB | $43 + $42 + $25 = **$110** |
| + CF Workers Paid | | $5 |
| + Better Stack | | $0–10 |
| **Итого MVP** | | **~$30/мес** |
| **Итого Production** | | **~$70/мес** |

**Плюсы:**
- Самое дешёвое из всех вариантов EU
- Доступ к dedicated bare metal (Robot) на следующем этапе — лучшее цена/производительность в индустрии
- У Тсерена уже есть Hetzner-аккаунт + tsekh-1 (NixOS+ZFS) → есть опыт
- Полный контроль над инфраструктурой

**Минусы:**
- Нужно администрировать самим: Postgres backup'ы, мониторинг, апдейты
- Нет managed Kubernetes (нужно поднимать k3s/k0s самим, или использовать Docker Compose)
- Менее масштабируемо при нагрузке > 10K пользователей (нужны кросс-региональные кластеры)
- Меньше DC, чем у Vultr/AWS/GCP (только EU фактически)

---

### Вариант B — Vultr (предложен Андреем)

**Регионы:** Amsterdam, Frankfurt, London, Paris, Stockholm + глобально.

| Этап | Конфигурация | Цена |
|------|--------------|------|
| **MVP (без K8s, Docker Compose)** | 4vCPU/8GB ($24) Postgres+Ory + 2vCPU/4GB ($12) bot+workers + Block storage 100GB ($10) | **$46** |
| **MVP (с VKE — Vultr Kubernetes Engine)** | VKE control $10 + 2 nodes 2vCPU/4GB ($24 каждая) + 100GB Block storage ($10) | **$68** |
| **Production** | 4vCPU/16GB ($48) Postgres + 2vCPU/4GB ($12) Ory + 2vCPU/4GB ($12) bot+workers + 200GB Block storage ($20) | **$92** |
| **Масштаб** | VKE + 3 nodes 4vCPU/8GB ($48 каждая) + 500GB Block ($50) + Managed DB ($60+) | **$254+** |
| + CF Workers Paid | | $5 |
| **Итого MVP** | | **~$50–75/мес** |
| **Итого Production** | | **~$100/мес** |

**Плюсы:**
- У Андрея уже есть Vultr-аккаунт и опыт развёртывания
- Есть managed Kubernetes (VKE) дешёвый ($10/мес control plane)
- Более широкая сеть DC (есть APAC регионы для глобального роста)
- Managed Database (Postgres) — $60+/мес, можно использовать вместо Neon

**Минусы:**
- В 2× дороже Hetzner на тех же конфигах
- Меньше готовых интеграций с инструментами enterprise (Datadog, Grafana Cloud и т.п.)
- VKE менее зрелый, чем GKE/EKS

---

### Вариант C — GKE Autopilot (Google Cloud) или EKS (AWS)

**Регионы GCP:** europe-west1 (Belgium), europe-west3 (Frankfurt), europe-west4 (Netherlands).
**Регионы AWS:** eu-central-1 (Frankfurt), eu-west-1 (Ireland), eu-west-2 (London).

#### GKE Autopilot (рекомендуем как cloud-вариант)

| Этап | Конфигурация | Цена |
|------|--------------|------|
| **MVP** | Autopilot pods 5vCPU/10GB constant + Cloud SQL db-g1-small Postgres + 50GB SSD + LB | ~$160 + $45 + $10 + $20 = **~$235** |
| **Production** | Autopilot 10vCPU/25GB + Cloud SQL n1-standard-2 + 200GB SSD + LB + replicas | ~$280 + $130 + $40 + $30 = **~$480** |
| **Масштаб** | Autopilot 30vCPU + Cloud SQL n1-standard-4 HA + cross-zone replicas | ~$700 + $400 + $100 = **~$1200** |
| + CF Workers Paid | | $5 |
| **Итого MVP** | | **~$240/мес** |
| **Итого Production** | | **~$485/мес** |

> **GCP free tier:** $300 кредитов на 90 дней для новых аккаунтов. Покрывает первый месяц MVP с запасом.

#### EKS (AWS) — для сравнения

| Этап | Конфигурация | Цена |
|------|--------------|------|
| **MVP** | EKS control $73 + 2 t3.medium nodes ($60) + RDS db.t3.small ($30) + EBS+ALB+egress | $73 + $60 + $30 + $30 = **~$195** |
| **Production** | EKS + 3 t3.large ($180) + RDS db.t3.medium ($60) + replicas | $73 + $180 + $60 + $60 = **~$375** |
| **Итого MVP** | | **~$200/мес** |
| **Итого Production** | | **~$380/мес** |

**Плюсы (GKE/EKS):**
- Управляемый K8s — apдейты, security patches, autoscaling вкл из коробки
- Масштабирование hands-off до 100K+ пользователей
- Любая Cloud-Native экосистема (Helm, Istio, Knative, ArgoCD) ставится за минуты
- SOC 2 / ISO 27001 / GDPR-attestation на уровне provider'а — упрощает продажу enterprise
- Multi-region failover настраивается стандартными средствами
- **Не переделывать при росте** — главный плюс под целевую модель Тсерена

**Минусы:**
- В 5–10× дороже Hetzner на MVP-стадии
- Серьёзная кривая обучения (особенно AWS) — Паше нужно будет инвестировать время
- Egress дорогой ($0.08–0.12/GB исходящего трафика — на 1TB ~$100/мес сверху)
- Vendor lock-in при использовании managed-фич (Cloud Spanner, Cloud Run, Lambda, …)
- Сложнее разобрать счёт — много мелких позиций

---

## 3. Сводная таблица

| Параметр | Hetzner | Vultr | GKE Autopilot | EKS |
|----------|---------|-------|---------------|-----|
| **MVP цена/мес** | $30 | $50–75 | $240 | $200 |
| **Production цена/мес** | $70 | $100 | $485 | $380 |
| **Масштаб (10K users)** | $110 | $250+ | $1200 | $1000 |
| **Регион EU** | ✅ DE/FI | ✅ NL/DE/UK | ✅ BE/DE/NL | ✅ DE/IE/UK |
| **Managed K8s** | ❌ (k3s самим) | ✅ VKE | ✅ Autopilot | ✅ EKS |
| **Managed Postgres** | ❌ self-hosted | ✅ Vultr DB | ✅ Cloud SQL | ✅ RDS |
| **Auto-scale** | ❌ ручное | ⚠️ ограничено | ✅ из коробки | ✅ из коробки |
| **Multi-region failover** | ⚠️ сложно | ⚠️ сложно | ✅ нативно | ✅ нативно |
| **GDPR attestation** | ⚠️ сами | ⚠️ сами | ✅ provider | ✅ provider |
| **SOC 2 / ISO 27001** | ❌ | ❌ | ✅ provider | ✅ provider |
| **YC investor optics** | средне | средне | **высоко** | **высоко** |
| **Кривая обучения** | низкая (Docker) | низкая | высокая | очень высокая |
| **Опыт в команде** | Тсерен (tsekh-1) | Андрей | нет | нет |
| **Free tier при старте** | ❌ | ❌ | ✅ $300/90 дней | ⚠️ только compute t-class |

---

## 4. Скрытые расходы

| Категория | Hetzner | Vultr | GKE | EKS |
|-----------|---------|-------|-----|-----|
| **Egress** (исходящий трафик) | 20TB включено | 1-10TB включено | $0.12/GB после 1GB | $0.09/GB после 1GB |
| **Egress 1TB/мес** | $0 | $0 (если в плане) | ~$120 | ~$90 |
| **Backup storage** | $4 (BX11) | $5–20 (Block) | в Cloud SQL | в RDS |
| **Load balancer** | $5–10 | $10 | $20+ | $20+ (ALB) |
| **Snapshot storage** | $0.011/GB | $0.05/GB | $0.04/GB | $0.05/GB |
| **NAT gateway** | бесплатно | бесплатно | $0.045/час | $0.045/час |

> **Важно:** для production-стадии egress на GCP/AWS может удвоить счёт. Hetzner включает 20TB egress в цену сервера — критическое преимущество при росте.

---

## 5. Рекомендация

### Если приоритет — «не переделывать при росте» (позиция Тсерена)

**→ GKE Autopilot.** Почему:
1. Autopilot биллит по реальному использованию (vCPU·сек + GB·сек), не за сами ноды — нет переплаты за idle
2. Free tier $300/90 дней покрывает MVP-эксперимент почти бесплатно
3. Cloud SQL — managed Postgres с EU-регионом, point-in-time recovery, автоматические бэкапы
4. Стоимость растёт линейно с пользователями, нет «ступенек» при масштабировании
5. Investor optics (YC, SOC 2 audit) — без работы со стороны команды
6. Опыт работы с GKE — востребованный skill, проще нанимать инженеров

**Когда GKE Autopilot становится дороже статической инфры:**
- > 10K constant активных пользователей с равномерной нагрузкой → bare metal Hetzner экономичнее
- Можно мигрировать в этой точке (через 2-3 года)

### Если приоритет — «минимальная стоимость до 1000 пользователей»

**→ Hetzner Cloud + CF Workers + Cloudflare R2 для backup.** Сэкономим $200–400/мес первые 6 месяцев.

### Если приоритет — «использовать опыт Андрея»

**→ Vultr с VKE.** Промежуточный вариант: managed K8s, но дешевле облаков.

---

## 6. Что предлагаю на встречу 14

1. **Принять решение:** GKE Autopilot vs Hetzner — на основе горизонта планирования. Если YC-заявка → демо Q4 2026 → пилот → масштаб 2027 — то GKE Autopilot оправдан. Если первая цель «работающий MVP до сентября» — Hetzner быстрее.
2. **Если GKE Autopilot:** активировать GCP free tier credits. Паша обучается базовому GKE (~1 неделя). Cloud SQL Postgres EU.
3. **Если Hetzner:** использовать существующий аккаунт Тсерена. Docker Compose на одной CX32 для старта. Миграция в k3s → GKE при росте.
4. **Не выбирать Vultr** — он не побеждает ни в одной категории (дороже Hetzner, менее зрелый чем GKE/EKS).
5. **EKS отбросить** — дороже GKE на сопоставимых конфигах + сложнее в эксплуатации, без преимуществ для нашего профиля.

---

## 7. Открытые вопросы для обсуждения

| # | Вопрос | Кто отвечает |
|---|--------|--------------|
| 1 | Горизонт планирования: цель до 2026-09 (MVP) или до 2027-Q2 (масштабирование)? | Тсерен |
| 2 | Бюджет инфры: $30/мес vs $250/мес — что приемлемо при текущем runway? | Тсерен (S0 неудовлетворённость) |
| 3 | YC заявка — есть ли требования к compliance (SOC 2)? | Тсерен |
| 4 | Опыт Паши с GKE/Cloud SQL — есть или нужно учиться? | Паша |
| 5 | Multi-region (US + EU) или только EU? | Тсерен (Track B стратегия) |
| 6 | Cloudflare R2 vs cloud-native storage — где бэкапы? | Андрей |
