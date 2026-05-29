---
type: doc
status: active
family: F9
kernel: C
system: C3
role: Operations
created: 2026-05-28
updated: 2026-05-28
owner: Церен
---

# Ильшат Габдуллин — доступы Track A

## Профиль

| Поле | Значение |
|------|----------|
| **ФИО** | Ильшат Габдуллин |
| **Email** | `igabdullin@gmail.com` |
| **Роль** | Владелец Track A |
| **Зона** | Продукт, инфраструктура, команда, приоритеты |
| **Дедлайн автономии** | 15 июля 2026 |
| **Source** | [WP-281](../../../../../../../0.OPS/0.9.Inbox/WP-281-track-a-transition-plan.md) |

---

## Мастер-таблица доступов

| # | Система | Статус | Инструкция по выдаче | Заметки |
|---|---------|--------|----------------------|---------|
| 1 | **GitHub** (6 репозиториев) | ✅ Выдано | Выполнено Kimi через `gh api` — admin на: `aisystant`, `aisystant-front`, `guides`, `personal-route-guide`, `iwe-starter`, `DS-ecosystem-development` | — |
| 2 | **Neon** (16 БД) | ✅ Выдано (admin) | 1. Зайти в [console.neon.tech](https://console.neon.tech) → проект → **Settings** → **Members** → **Invite** → `igabdullin@gmail.com` → роль **Admin** или **Editor** | Event sourcing, bounded contexts |
| 3 | **Railway** | ✅ Выдано (admin, все проекты Track A) | 1. [dashboard.railway.app](https://dashboard.railway.app) → проект → **Settings** → **Members** → **Invite** → `igabdullin@gmail.com` → роль **Admin** | Python-сервисы, Chatwoot, n8n |
| 4 | **Cloudflare** (Track A) | ⬜ Нужно выдать | 1. [dash.cloudflare.com](https://dash.cloudflare.com) → аккаунт → **Manage account** → **Members** → **Invite** → `igabdullin@gmail.com` → роль **Administrator** | Workers, домены, DNS |
| 5 | **VK Cloud Ory** | ⬜ Нужно выдать | 1. [cloud.vk.com](https://cloud.vk.com) → проект → **Управление доступом** → **Добавить пользователя** → email или VK ID → роль **Администратор** | Авторизация (Kratos/Hydra/Keto) |
| 6 | **Better Stack** | ✅ Выдано (admin) | 1. [betterstack.com](https://betterstack.com) → **Team Settings** → **Invite member** → `igabdullin@gmail.com` → роль **Admin** или **Owner** | Мониторинг, алерты, статус-страницы |
| 7 | **1Password** (vault «IWE secrets») | ⬜ Нужно выдать | 1. [1password.com](https://1password.com) → vault **«IWE secrets»** → **Manage access** → **Invite** → `igabdullin@gmail.com` → роль **Manager** (чтобы мог читать и добавлять, но не удалять vault) | Секреты, API-токены, пароли |
| 8 | **Metabase** | ⬜ Нужно выдать | 1. Открыть instance Metabase (URL в Railway) → шестерёнка **Admin** → **People** → **Invite** → `igabdullin@gmail.com` → группа **All Users** + дать доступ к коллекциям аналитики | Аналитика, дашборды |
| 9 | **Directus** | ⬜ Нужно выдать | 1. Открыть instance Directus (URL в Railway) → **Settings** → **Users** → **Create user** → `igabdullin@gmail.com` → роль **Admin** или кастомная роль с правами на CRM | CRM, конфигурация баллов |
| 10 | **Chatwoot** (self-hosted) | ✅ Выдано (administrator через super_admin/users) | 1. Открыть instance Chatwoot (URL в Railway) → **Settings** → **Agents** → **Add agent** → `igabdullin@gmail.com` → роль **Administrator** | Поддержка, тикеты |
| 11 | **n8n** | ✅ Выдано (owner/admin) | 1. Открыть instance n8n (URL в Railway) → **Settings** → **Users** → **Invite** → `igabdullin@gmail.com` → роль **Owner** или **Admin** | Автоматизация, Светофор, health probes |
| 12 | **Telegram** (IT-группы) | ✅ Выдано (добавлен в группы) | 1. Добавить `@igabdullin` (username) или номер телефона в группы: **IT-ops**, **Alerts (Better Stack)**, **Команда Track A** | Алерты, оперативка |

---

## Чек-лист выдачи

- [x] GitHub (6 репозиториев) — admin
- [x] Neon — admin
- [x] Railway — admin (все проекты Track A)
- [ ] Cloudflare — administrator
- [ ] VK Cloud Ory — администратор
- [x] Better Stack — admin
- [ ] 1Password (IWE secrets) — manager
- [ ] Metabase — admin
- [ ] Directus — admin
- [x] Chatwoot — administrator (super_admin/users)
- [x] n8n — owner/admin
- [x] Telegram — добавлен в группы

---

## Связанные документы

- [WP-281 Track A — план перехода](../../../../../../../0.OPS/0.9.Inbox/WP-281-track-a-transition-plan.md)
- [Мастер-реестр команды](../../../../../../../A.Systems-Builder/A3.Aisystant-Ecosystem-Builder/A3.3.Operations/3.3.1.%20Team-and-Roles/Карта%20ролей%20и%20ответственности%203.3.md)
