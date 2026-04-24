#!/usr/bin/env bash
# replay.sh — Replay a build from a recorded SHA log
#
# Clones or updates all repos and pins each to the exact SHA recorded
# in a previous build-all.sh run. Guarantees byte-for-byte identical
# source inputs to the Maven build.
#
# Usage:
#   ./replay.sh build-logs/20260424T143022.shas
#   ./replay.sh build-logs/20260424T143022.shas -DskipTests

set -euo pipefail

LOG_FILE="${1:?Usage: replay.sh <sha-log-file> [mvn args...]}"
shift || true   # remaining args passed to mvn

ORG="casehubio"

if [ ! -f "$LOG_FILE" ]; then
  echo "ERROR: log file not found: $LOG_FILE" >&2
  exit 1
fi

echo "==> Replaying build from: $LOG_FILE"
echo ""
grep "^#" "$LOG_FILE" | sed 's/^# /    /'
echo ""

# ── Clone/update and pin each repo ────────────────────────────────────────
echo "==> Checking out recorded SHAs..."
while IFS='=' read -r repo sha; do
  [[ "$repo" =~ ^#.*$ || -z "$repo" ]] && continue
  if [ ! -d "$repo/.git" ]; then
    printf "    %-20s cloning...\n" "$repo"
    git clone --quiet "https://github.com/$ORG/$repo.git"
  fi
  git -C "$repo" fetch --quiet origin
  git -C "$repo" checkout --quiet --detach "$sha"
  printf "    %-20s %s\n" "$repo" "$sha"
done < "$LOG_FILE"

# ── Build ──────────────────────────────────────────────────────────────────
echo ""
echo "==> Building..."
echo ""
mvn install -f aggregator.xml "$@"

echo ""
echo "==> Replay complete."
