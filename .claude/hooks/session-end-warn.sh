#!/usr/bin/env bash
# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Warn at session end if workbench/ has stale content (>7 days, no matching archive).

set -e

command -v jq >/dev/null || exit 0

payload=$(cat)
cwd=$(echo "$payload" | jq -r '.cwd // "."')

wb="$cwd/workbench"

[ -d "$wb" ] || exit 0

stale_count=0
while IFS= read -r _; do
  stale_count=$((stale_count + 1))
done < <(find "$wb" -type f -mtime +7 2>/dev/null)

if [ "$stale_count" -gt 0 ]; then
  echo "[v6] Stale workbench: $stale_count files in $wb older than 7 days. Run /v6-feature ship phase or move to archive/ manually." >&2
fi

exit 0
