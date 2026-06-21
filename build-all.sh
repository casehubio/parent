#!/usr/bin/env bash
# build-all.sh — Full-stack casehubio incremental build
#
# Module list, dependency graph, and build order are read from:
#   build/modules-core.csv       — core CI+local modules
#   build/modules-applications.csv — application modules (opt-in)
#   build/modules-local.csv      — local-only modules (not built in CI)
#
# Each CSV row: name,dep1,dep2,...  (row order = build order)
#
# Usage:
#   ./build-all.sh                  # incremental build
#   ./build-all.sh --no-cache       # force full rebuild
#   ./build-all.sh --skip-tests
#   ./build-all.sh --include-apps   # also build application modules
#   ./build-all.sh -T 1C            # extra Maven args

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/build-logs"
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
LOG_FILE="$LOG_DIR/$TIMESTAMP.shas"

# ── Exception maps (deviations from convention) ───────────────────────────────
# Default: local path = ../<name>, GitHub repo = casehubio/<name>

declare -A PATH_OVERRIDE=(
  [quarkus-langchain4j]="../../quarkus-langchain4j"
  [drafthouse]="../drafthouse/server"
)
declare -A REPO_OVERRIDE=(
  [pages]="casehub-pages"
  [desiredstate]="casehub-desiredstate"
  [ras]="casehub-ras"
  [ops]="casehub-ops"
)
# quarkus-langchain4j is under a different GitHub org
declare -A ORG_OVERRIDE=(
  [quarkus-langchain4j]="quarkusio"
)

# ── Load modules from CSV ─────────────────────────────────────────────────────

declare -a REPOS=()
declare -A DEPS=()

load_csv() {
  local csv=$1
  while IFS=',' read -r name rest; do
    [[ "$name" =~ ^#|^[[:space:]]*$ ]] && continue
    # Trim inline comments from rest (everything after #)
    rest="${rest%%#*}"
    REPOS+=("$name")
    # Trim whitespace from deps
    IFS=',' read -ra dep_arr <<< "$rest"
    local deps_clean=()
    for d in "${dep_arr[@]}"; do
      d="${d// /}"  # strip spaces
      [[ -n "$d" ]] && deps_clean+=("$d")
    done
    DEPS[$name]="${deps_clean[*]:-}"
  done < "$csv"
}

# Parse flags
NO_CACHE=false
SKIP_TESTS=false
INCLUDE_APPS=false
MVN_ARGS=()
for arg in "$@"; do
  case "$arg" in
    --no-cache)      NO_CACHE=true ;;
    --skip-tests)    SKIP_TESTS=true ;;
    --include-apps)  INCLUDE_APPS=true ;;
    *)               MVN_ARGS+=("$arg") ;;
  esac
done

load_csv "$SCRIPT_DIR/build/modules-local.csv"
load_csv "$SCRIPT_DIR/build/modules-core.csv"
if [ "$INCLUDE_APPS" = true ]; then
  load_csv "$SCRIPT_DIR/build/modules-applications.csv"
fi

# ── Helpers ──────────────────────────────────────────────────────────────────

local_path() {
  local name=$1
  echo "${PATH_OVERRIDE[$name]:-../$name}"
}

gh_repo() {
  local name=$1
  local org="${ORG_OVERRIDE[$name]:-casehubio}"
  local repo="${REPO_OVERRIDE[$name]:-$name}"
  echo "$org/$repo"
}

# ── Setup ────────────────────────────────────────────────────────────────────

mkdir -p "$LOG_DIR"
{ echo "# casehubio full-stack build"; echo "# timestamp: $TIMESTAMP"; echo ""; } > "$LOG_FILE"

# Load previous cache
declare -A PREV_SHA
LAST_LOG=$(ls -1t "$LOG_DIR"/*.shas 2>/dev/null | grep -v "$LOG_FILE" | head -1 || true)
if [ -n "$LAST_LOG" ] && [ "$NO_CACHE" = false ]; then
  echo "==> Cache: $LAST_LOG"
  while IFS='=' read -r repo sha; do
    [[ "$repo" =~ ^#|^[[:space:]]*$ ]] && continue
    PREV_SHA[$repo]=$sha
  done < "$LAST_LOG"
else
  echo "==> Cache: none (full rebuild)"
fi

# ── Step 1: Clone or update ──────────────────────────────────────────────────
echo ""; echo "==> Fetching repos..."
for repo in "${REPOS[@]}"; do
  dir="$(local_path "$repo")"
  if [ -d "$dir/.git" ]; then
    printf "    %-30s updating\n" "$repo"
    git -C "$dir" fetch --quiet origin main
    git -C "$dir" reset --quiet --hard origin/main
  else
    gh_url="https://github.com/$(gh_repo "$repo").git"
    printf "    %-30s cloning into %s\n" "$repo" "$dir"
    mkdir -p "$(dirname "$dir")"
    git clone --quiet "$gh_url" "$dir"
  fi
done

# ── Step 2: Record SHAs ──────────────────────────────────────────────────────
echo ""; echo "==> Recording SHAs..."
declare -A CURR_SHA
for repo in "${REPOS[@]}"; do
  sha=$(git -C "$(local_path "$repo")" rev-parse HEAD)
  CURR_SHA[$repo]=$sha
  echo "$repo=$sha" >> "$LOG_FILE"
  printf "    %-30s %s\n" "$repo" "$sha"
done

# ── Step 3: Pin to SHAs ──────────────────────────────────────────────────────
for repo in "${REPOS[@]}"; do
  git -C "$(local_path "$repo")" checkout --quiet --detach "${CURR_SHA[$repo]}"
done

# ── Step 4: Classify ─────────────────────────────────────────────────────────
echo ""; echo "==> Incremental analysis..."
declare -A STATE
for repo in "${REPOS[@]}"; do
  curr="${CURR_SHA[$repo]}"; prev="${PREV_SHA[$repo]:-}"
  if [ "$curr" != "$prev" ] || [ "$NO_CACHE" = true ]; then
    STATE[$repo]=build
    printf "    %-30s BUILD\n" "$repo"
    continue
  fi
  dep_built=false
  for dep in ${DEPS[$repo]:-}; do
    [ "${STATE[$dep]:-skip}" != "skip" ] && dep_built=true && break
  done
  if [ "$dep_built" = true ]; then
    STATE[$repo]=test; printf "    %-30s TEST\n" "$repo"
  else
    STATE[$repo]=skip; printf "    %-30s SKIP\n" "$repo"
  fi
done

# ── Step 5: Build ────────────────────────────────────────────────────────────
# pages is yarn-only — not in aggregator.xml
if [ "${STATE[pages]:-skip}" = "build" ]; then
  echo ""; echo "==> Building pages (yarn)"
  (cd "$(local_path pages)" && yarn install && yarn build)
fi

BUILD_LIST=""
for repo in "${REPOS[@]}"; do
  [ "$repo" = "pages" ] && continue
  [ "${STATE[$repo]:-skip}" = "build" ] && BUILD_LIST="${BUILD_LIST:+$BUILD_LIST,}$(local_path "$repo")"
done
echo ""
if [ -n "$BUILD_LIST" ]; then
  echo "==> Installing: $BUILD_LIST"
  mvn install -f "$SCRIPT_DIR/aggregator.xml" -pl "$BUILD_LIST" "${MVN_ARGS[@]}"
else
  echo "==> Nothing to build."
fi

# ── Step 6: Test ─────────────────────────────────────────────────────────────
TEST_LIST=""
for repo in "${REPOS[@]}"; do
  [ "$repo" = "pages" ] && continue
  [ "${STATE[$repo]:-skip}" = "test" ] && TEST_LIST="${TEST_LIST:+$TEST_LIST,}$(local_path "$repo")"
done
if [ -n "$TEST_LIST" ] && [ "$SKIP_TESTS" = false ]; then
  echo ""; echo "==> Retesting: $TEST_LIST"
  mvn test -f "$SCRIPT_DIR/aggregator.xml" -pl "$TEST_LIST" "${MVN_ARGS[@]}"
fi

echo ""
echo "==> Done. SHA log: $LOG_FILE"
