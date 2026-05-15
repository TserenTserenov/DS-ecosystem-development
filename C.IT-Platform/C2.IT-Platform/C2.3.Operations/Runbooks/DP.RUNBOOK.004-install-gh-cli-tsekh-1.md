---
type: runbook
id: DP.RUNBOOK.004
title: "Установка GitHub CLI (gh) на tsekh-1"
scope: infrastructure
host: tsekh-1
status: active
created: 2026-05-15
---

# DP.RUNBOOK.004 — Установка GitHub CLI (gh) на tsekh-1

## Зачем

GitHub CLI (`gh`) необходим для:
- **D1** Dependabot alerts — `gh api /repos/{owner}/{repo}/dependabot/alerts`
- **D3** TruffleHog CI runs — `gh run list --workflow=secret-scan.yml`
- **Branch protection verification** — `gh api /repos/{owner}/{repo}/branches/main/protection`

Без `gh` аудитор VR.R.002 не может верифицировать CI/CD security coverage (раздел D B7.4), что создаёт **verification gap** (flag L1).

## Предусловия

- SSH-доступ к tsekh-1 (`ssh tsekh-1` или аналог)
- GitHub Personal Access Token (PAT) с scope:
  - `repo` (для private repos)
  - `dependabot:read` (для Dependabot alerts)
  - `actions:read` (для CI run статуса)

## Установка

### Шаг 1. Установить gh CLI

Вариант A — через nix (если tsekh-1 на NixOS / nix-env):

```bash
nix-env -iA nixpkgs.gh
```

Вариант B — через официальный скрипт (универсальный):

```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

Вариант C — через snap:

```bash
sudo snap install gh
```

Проверка:

```bash
gh --version
```

### Шаг 2. Аутентификация

```bash
gh auth login
```

- Выбрать **GitHub.com**
- Выбрать **HTTPS**
- Выбрать **Paste an authentication token**
- Вставить PAT

Или non-interactive (для systemd / cron):

```bash
export GH_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
gh auth status
```

### Шаг 3. Проверка Dependabot (тест D1)

```bash
gh api /repos/TserenTserenov/knowledge-mcp/dependabot/alerts --jq '. | length'
gh api /repos/TserenTserenov/activity-hub/dependabot/alerts --jq '. | length'
```

Ожидаемый результат: число (0 или больше), не "404" и не "Unauthorized".

### Шаг 4. Проверка CI runs (тест D3)

```bash
gh run list --repo=TserenTserenov/knowledge-mcp --workflow=secret-scan.yml --limit=1
gh run list --repo=TserenTserenov/activity-hub --workflow=secret-scan.yml --limit=1
```

Ожидаемый результат: список запусков со статусом `completed` + `success`.

## Постусловия

После установки и проверки:
- [ ] Обновить `security-posture.md` §D: `gh CLI ✅ установлен`
- [ ] Следующий daily audit (04:45 МСК) автоматически получит D1/D3 coverage
- [ ] Flag L1 закроется самостоятельно при следующем аудите

## Rollback

```bash
# nix
nix-env --uninstall gh

# apt
sudo apt remove gh
```

## Ссылки

- B7.4-external-audit-checklist.md §D
- security-posture.md §D CI/CD Security Coverage
- Аудит-отчёт 2026-05-15 flag L1
