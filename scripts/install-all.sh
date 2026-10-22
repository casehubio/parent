#!/bin/bash
# Install all ecosystem repos to .m2 in dependency order.
# Uses individual mvn install per repo (not the aggregator) so the
# flatten-maven-plugin resolves ${revision} correctly in each POM.
#
# Usage: install-all.sh [--skip-tests] [--quiet]

set -euo pipefail

CASEHUB="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(dirname "$CASEHUB")"
MVN="${MVN:-/opt/homebrew/bin/mvn}"
ARGS="--batch-mode"

for arg in "$@"; do
  case "$arg" in
    --skip-tests) ARGS="$ARGS -DskipTests" ;;
    --quiet)      ARGS="$ARGS -q" ;;
  esac
done

REPOS=(
  parent
  platform
  worker
  ledger
  connectors
  neocortex
  eidos
  desiredstate
  ras
  qhorus
  work
  engine
  agency
  casehub-langchain4j
  workers
  claudony
  ops
  iot
  openclaw
  devtown
  aml
  clinical
  life
  soc
  fsitrading
  quarkmind
  scaffold
)

PASS=0
FAIL=0
SKIP=0

for repo in "${REPOS[@]}"; do
  dir="$ROOT/$repo"
  if [ ! -f "$dir/pom.xml" ]; then
    echo "SKIP  $repo (no pom.xml)"
    SKIP=$((SKIP + 1))
    continue
  fi
  echo -n "BUILD $repo ... "
  if $MVN install -f "$dir/pom.xml" $ARGS > /dev/null 2>&1; then
    echo "OK"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
done

echo ""
echo "$PASS passed, $FAIL failed, $SKIP skipped"
exit $FAIL
