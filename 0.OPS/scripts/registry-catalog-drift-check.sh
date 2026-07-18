#!/usr/bin/env bash
# registry-catalog-drift-check.sh — E2 drift guard для каталога реестров.
# Падает, если коммит/PR ДОБАВЛЯЕТ новый файл-реестр (*-catalog.yaml / *registry*.yaml)
# без правки самого каталога — то есть «новый реестр без записи в каталоге».
# Зеркало WP-REGISTRY ↔ inbox drift-guard (commit-msg хук DS-my-strategy).
# Метод: DP.METHOD.054 §8. WP-419, peer-session 2026-06-14-03.
#
# Использование:
#   CI:     BASE_REF=<sha> bash registry-catalog-drift-check.sh
#   тест:   bash registry-catalog-drift-check.sh <added-list-file> <changed-list-file>
set -euo pipefail

CATALOG="0.OPS/WP-419-registry-catalog-draft.yaml"
REGISTRY_RE='(-catalog\.yaml|registry.*\.yaml)$'

if [ "${1:-}" != "" ] && [ "${2:-}" != "" ]; then
  # Тестовый режим: списки переданы файлами.
  ADDED=$(cat "$1")
  CHANGED=$(cat "$2")
else
  # CI/git-режим: считаем diff против базы.
  BASE="${BASE_REF:-}"
  # event.before на первом push ветки = нули → откатываемся на предыдущий коммит.
  if [ -z "$BASE" ] || ! git rev-parse --verify --quiet "$BASE^{commit}" >/dev/null 2>&1; then
    BASE=$(git rev-parse --verify --quiet "HEAD~1" || git rev-parse HEAD)
  fi
  ADDED=$(git diff --name-only --diff-filter=A "$BASE...HEAD" 2>/dev/null || true)
  CHANGED=$(git diff --name-only "$BASE...HEAD" 2>/dev/null || true)
fi

# Новые файлы-реестры (добавленные), исключая сам каталог.
NEW_REGISTRIES=$(printf '%s\n' "$ADDED" | grep -E "$REGISTRY_RE" | grep -vF "$CATALOG" || true)

if [ -z "$NEW_REGISTRIES" ]; then
  echo "✅ registry-catalog drift: новых реестров не добавлено"
  exit 0
fi

# Каталог тронут в этом же изменении?
if printf '%s\n' "$CHANGED" | grep -qF "$CATALOG"; then
  echo "✅ registry-catalog drift: новый реестр сопровождён правкой каталога"
  exit 0
fi

echo "❌ Новый реестр добавлен без записи в каталоге реестров:"
printf '%s\n' "$NEW_REGISTRIES" | sed 's/^/   /'
echo ""
echo "   Добавь запись в $CATALOG"
echo "   (поля: name / owner / code_scheme / sot_path / update_mechanism / status / tier)."
echo "   Основание: DP.METHOD.054 §8 «новый реестр = запись в каталоге + namespace в реестре нумераций»."
exit 1
