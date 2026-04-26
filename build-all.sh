#!/usr/bin/env bash
# build-all.sh — Full-stack casehubio incremental build
#
# Determines what to do for each module based on SHA changes since the last
# successful build:
#
#   BUILD — own SHA changed → full compile + test + install
#   TEST  — own SHA unchanged but a transitive dep changed → test only (no recompile)
#   SKIP  — own SHA and all deps unchanged → skip entirely (artifact in .m2 is current)
#
# The most recent build log (build-logs/*.shas) acts as the cache manifest.
# replay.sh reproduces any prior build exactly from its SHA log.
#
# Usage:
#   ./build-all.sh                  # incremental build
#   ./build-all.sh --no-cache       # force full rebuild ignoring cache
#   ./build-all.sh --skip-tests     # skip tests even for TEST-state modules
#   ./build-all.sh -DskipTests      # pass-through to mvn (skips all tests)
#   ./build-all.sh -T 1C            # parallel build (mvn pass-through)

set -euo pipefail

ORG="casehubio"
BRANCH="main"
LOG_DIR="build-logs"
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
LOG_FILE="$LOG_DIR/$TIMESTAMP.shas"

# ── Dependency graph ────────────────────────────────────────────────────────
# Direct casehub dependencies per repo. Transitive deps are resolved by
# walking the graph — if a dep is in BUILD state, all consumers are at least
# in TEST state.
declare -A DEPS
DEPS[quarkus-langchain4j]=""
DEPS[quarkus-ledger]=""
DEPS[casehub-connectors]=""
DEPS[quarkus-work]="quarkus-ledger casehub-connectors"
DEPS[quarkus-qhorus]="quarkus-ledger quarkus-work"
DEPS[casehub-engine]="quarkus-langchain4j quarkus-ledger quarkus-work"
DEPS[claudony]="quarkus-ledger quarkus-work quarkus-qhorus"

# Build order — topological from the dependency graph
# quarkus-langchain4j: fork of upstream, publishes 999-SNAPSHOT to GitHub Packages.
# No casehub deps, so it builds first alongside quarkus-ledger.
REPOS=(
  quarkus-langchain4j
  quarkus-ledger
  casehub-connectors
  quarkus-work
  quarkus-qhorus
  casehub-engine
  claudony
)

# ── Parse flags ─────────────────────────────────────────────────────────────
NO_CACHE=false
SKIP_TESTS=false
MVN_ARGS=()
for arg in "$@"; do
  case "$arg" in
    --no-cache)    NO_CACHE=true ;;
    --skip-tests)  SKIP_TESTS=true ;;
    *)             MVN_ARGS+=("$arg") ;;
  esac
done

mkdir -p "$LOG_DIR"

{
  echo "# casehubio full-stack build"
  echo "# timestamp: $TIMESTAMP"
  echo "# branch:    $BRANCH"
  echo ""
} > "$LOG_FILE"

# ── Load previous build cache ───────────────────────────────────────────────
declare -A PREV_SHA
LAST_LOG=$(ls -1t "$LOG_DIR"/*.shas 2>/dev/null | grep -v "$LOG_FILE" | head -1 || true)
if [ -n "$LAST_LOG" ] && [ "$NO_CACHE" = false ]; then
  echo "==> Cache: $LAST_LOG"
  while IFS='=' read -r repo sha; do
    [[ "$repo" =~ ^#.*$ || -z "$repo" ]] && continue
    PREV_SHA[$repo]=$sha
  done < "$LAST_LOG"
else
  echo "==> Cache: none (full rebuild)"
fi

# ── Step 1: Clone or update ─────────────────────────────────────────────────
echo ""
echo "==> Fetching repos from $ORG..."
for repo in "${REPOS[@]}"; do
  if [ -d "$repo/.git" ]; then
    printf "    %-20s updating\n" "$repo"
    git -C "$repo" fetch --quiet origin "$BRANCH"
    git -C "$repo" checkout --quiet "$BRANCH"
    git -C "$repo" reset --quiet --hard "origin/$BRANCH"
  else
    printf "    %-20s cloning\n" "$repo"
    git clone --quiet "https://github.com/$ORG/$repo.git"
  fi
done

# ── Step 2: Record current SHAs ─────────────────────────────────────────────
echo ""
echo "==> Recording SHAs..."
declare -A CURR_SHA
for repo in "${REPOS[@]}"; do
  sha=$(git -C "$repo" rev-parse HEAD)
  CURR_SHA[$repo]=$sha
  echo "$repo=$sha" >> "$LOG_FILE"
  printf "    %-20s %s\n" "$repo" "$sha"
done

# ── Step 3: Pin to recorded SHAs ────────────────────────────────────────────
for repo in "${REPOS[@]}"; do
  git -C "$repo" checkout --quiet --detach "${CURR_SHA[$repo]}"
done

# ── Step 4: Classify each module ────────────────────────────────────────────
# State per module:
#   build — own SHA changed → full compile + install + test
#   test  — own SHA unchanged but a dep is in build state → test only
#   skip  — nothing changed
#
# Walk in dependency order so dep state is known before consumer state.
echo ""
echo "==> Incremental analysis..."

declare -A STATE   # build | test | skip

for repo in "${REPOS[@]}"; do
  curr="${CURR_SHA[$repo]}"
  prev="${PREV_SHA[$repo]:-}"

  if [ "$curr" != "$prev" ] || [ "$NO_CACHE" = true ]; then
    STATE[$repo]=build
    printf "    %-20s BUILD   (own SHA changed)\n" "$repo"
    continue
  fi

  dep_built=false
  for dep in ${DEPS[$repo]}; do
    if [ "${STATE[$dep]:-skip}" = "build" ] || [ "${STATE[$dep]:-skip}" = "test" ]; then
      dep_built=true
      break
    fi
  done

  if [ "$dep_built" = true ]; then
    STATE[$repo]=test
    printf "    %-20s TEST    (dep changed, rerun tests against new artifacts)\n" "$repo"
  else
    STATE[$repo]=skip
    printf "    %-20s SKIP    (SHA and all deps unchanged)\n" "$repo"
  fi
done

# ── Step 5: Build phase — full install for BUILD modules ─────────────────────
BUILD_LIST=""
for repo in "${REPOS[@]}"; do
  [ "${STATE[$repo]}" = "build" ] && BUILD_LIST="${BUILD_LIST:+$BUILD_LIST,}$repo"
done

echo ""
if [ -n "$BUILD_LIST" ]; then
  echo "==> Installing: $BUILD_LIST"
  mvn install -f aggregator.xml \
    -pl "$BUILD_LIST" \
    "${MVN_ARGS[@]}"
else
  echo "==> No modules need building."
fi

# ── Step 6: Test phase — test-only for TEST modules ──────────────────────────
TEST_LIST=""
for repo in "${REPOS[@]}"; do
  [ "${STATE[$repo]}" = "test" ] && TEST_LIST="${TEST_LIST:+$TEST_LIST,}$repo"
done

if [ -n "$TEST_LIST" ] && [ "$SKIP_TESTS" = false ]; then
  echo ""
  echo "==> Retesting against updated deps: $TEST_LIST"
  mvn test -f aggregator.xml \
    -pl "$TEST_LIST" \
    "${MVN_ARGS[@]}"
elif [ -n "$TEST_LIST" ] && [ "$SKIP_TESTS" = true ]; then
  echo ""
  echo "==> Skipping tests for: $TEST_LIST (--skip-tests)"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
if [ -z "$BUILD_LIST" ] && [ -z "$TEST_LIST" ]; then
  echo "==> All modules up to date. Nothing to do."
else
  echo "==> Done."
  [ -n "$BUILD_LIST" ] && echo "    Built:   $BUILD_LIST"
  [ -n "$TEST_LIST"  ] && echo "    Tested:  $TEST_LIST"
fi
echo "    SHA log: $LOG_FILE"
