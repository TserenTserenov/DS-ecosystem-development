---
family: F8
kernel: C
system: C2
role: Operations
status: active
title: "Platform Ops Dashboard — точка входа для наблюдаемости"
wp: WP-302
created: 2026-05-14
target_audience:
  - "Команда разработки"
  - "Дежурный оператор"
  - "Архитектор"
---

# Platform Ops Dashboard

> Единая точка входа: все инструменты наблюдаемости платформы в одном месте.
> Не дублирует данные — только ссылки и контекст «что смотреть где».

---

## 🟢 Uptime & Доступность

| Сервис | Инструмент | Ссылка | Что показывает |
|--------|-----------|--------|----------------|
| Все сервисы | **BetterUptime** | [aisystant.betteruptime.com](https://aisystant.betteruptime.com) | Публичный статус, SLA, incident history |
| Статус в TG | **Telegram** | [@aisystant_status](https://t.me/aisystant_status) | Алерты о падениях |
| Бот прод (health) | **Health endpoint** | [aist-bot-newarchitecture-production.up.railway.app/health](https://aist-bot-newarchitecture-production.up.railway.app/health) | HTTP 200 = бот жив |
| Бот пилот (health) | **Health endpoint** | [aistpilotbot-production.up.railway.app/health](https://aistpilotbot-production.up.railway.app/health) | HTTP 200 = пилот жив |

---

## 📊 Метрики & Данные

| Инструмент | Ссылка | Что показывает |
|-----------|--------|----------------|
| **Metabase** | [dashboard/2](https://metabase-production-a4f6.up.railway.app/dashboard/2) | Пользовательские метрики (ступени, активность, баллы) |
| **Grafana** | `TODO: вставить URL` | Latency, error rates, Neon connection pools |
| **Neon Console** | [console.neon.tech](https://console.neon.tech) | 15 БД, connection stats, query inspector |

---

## 🚀 Деплои & CI/CD

| Сервис | Инструмент | Что смотреть |
|--------|-----------|-------------|
| Railway workers (B1, B2, W1-W4) | **Railway** → [peaceful-vision](https://railway.app) | Deploy logs, env vars, redeploy status |
| CF Workers (10 репо: M1-M11) | **Cloudflare Dashboard** | Requests, errors, Worker logs |
| CF Workers CI | **GitHub Actions** (каждый репо `aisystant/*`) | Workflow runs → `cloudflare/wrangler-action@v3` |
| Railway — Metabase | Railway → [peaceful-vision](https://railway.app) | Сервис `metabase-production-a4f6` |

---

## 🔐 Безопасность & Compliance

| Документ | Путь | Что показывает |
|---------|------|----------------|
| **Security Posture Dashboard** | [security-posture.md](../C2.2.Architecture/security-posture.md) | Security maturity (1-3), WP-212 прогресс, open vulns |
| **12-factor Compliance Matrix** | [12factor-matrix.md](../C2.2.Architecture/12factor-matrix.md) | 31 сервис × 12 факторов, ✅/⚠️/❌ |
| **12-factor Posture Summary** | [12factor-report-wp307.md](../C2.2.Architecture/12factor-report-wp307.md) | WP-307 итоговый отчёт (May 2026) |

---

## 🗓️ Инцидент-лог

| Файл | Что содержит |
|------|-------------|
| [Incidents/](Incidents/) | Журнал инцидентов (разбор + timeline) |
| [Runbooks/](Runbooks/) | Процедуры реагирования (бот, OAuth, БД) |

---

## 🔄 Автоматические проверки (tsekh-1, 04:45 МСК)

| Скрипт | Что проверяет | Результат |
|--------|-------------|----------|
| `iwe-overnight-auditor.sh` | Security (B7.4 A-D) + 12-factor re-audit | `compliance_audits` в Neon `health` БД |
| `12factor-reaudit.sh` | F1/F5 (deploy.yml), F2 (manifests), F3 (.env.example), F11 (print()) | `12factor-report.json` |

---

## 📋 Контекст WP-302

Этот документ закрывает **WP-302 Ф4** (Platform Observability) на уровне «агрегатор ссылок».
Следующий шаг WP-302: Ф1 (Data Contract) → Personal Insight API → Bot/VS Code/Web каналы.

Связанные РП: WP-121 (learning data), WP-212 (security), WP-307 (12-factor), WP-296 (club connector).
