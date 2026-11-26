#!/usr/bin/env bash
# build-all.sh — Full-stack casehubio incremental build
#
# Module list, dependency graph, and build order are read from:
#   build/modules-core.csv       — foundation/orchestration/integration modules
#   build/modules-applications.csv — application modules
#
# Each CSV row: name,dep1,dep2,...  (row order = build order)
#
# Usage:
#   ./build-all.sh                  # incremental build
#   ./build-all.sh --no-cache       # force full rebuild
#   ./build-all.sh --skip-tests
#   ./build-all.sh --local          # build from current checkout (no fetch/reset)
#   ./build-all.sh -T 1C            # extra Maven args
#
# Inside an isx container, --local is auto-detected (ISX_CONTAINER is set).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Quick help — must run before declare -A (set -u conflicts with array literals)
for a in "$@"; do
  if [[ "$a" == "--help" || "$a" == "-h" ]]; then
    cat <<'HELP'
Usage: ./build-all.sh [OPTIONS] [MAVEN_ARGS...]

Clones all casehubio repos (or updates existing), then builds the full
ecosystem in dependency order. Incremental by default.

Modes:
  (default)          Incremental — clone/update, detect changes, build changed
  --aggregate        Single Maven reactor via aggregator.xml (fastest for clean setup)
  --no-cache         Ignore incremental cache, rebuild everything
  --local            Build from current checkout (no git fetch/reset)

Options:
  --skip-tests       Pass -DskipTests to Maven
  --head             Clone/checkout HEAD of each repo (default: verified SHAs from casehub-all)
  --help, -h         Show this help

Extra Maven args: ./build-all.sh --skip-tests -T 1C
HELP
    echo ""
    echo "Prerequisites:"
    for cmd in java mvn git node yarn; do
      if command -v "$cmd" > /dev/null 2>&1; then
        printf "  ✓ %s\n" "$cmd"
      else
        printf "  ✗ %s (not found)\n" "$cmd"
      fi
    done
    exit 0
  fi
done
LOG_DIR="$SCRIPT_DIR/build-logs"
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
LOG_FILE="$LOG_DIR/$TIMESTAMP.shas"

# ── Exception maps (deviations from convention) ───────────────────────────────
# Default: local path = ../<name>, GitHub repo = casehubio/<name>

declare -A PATH_OVERRIDE=(
  [quarkus-langchain4j]="../../quarkus-langchain4j"
  [drafthouse]="../drafthouse/server"
)
declare -A GIT_PATH_OVERRIDE=(
  [drafthouse]="../drafthouse"
)
declare -A REPO_OVERRIDE=(
  [worker]="casehub-worker"
  [pages]="casehub-pages"
  [desiredstate]="casehub-desiredstate"
  [ras]="casehub-ras"
  [ops]="casehub-ops"
)
# quarkus-langchain4j is under a different GitHub org
declare -A ORG_OVERRIDE=(
  [quarkus-langchain4j]="quarkusio"
  [casehub-mosaic]="mdproctor"
  [fsitrading]="mdproctor"
  [soc]="mdproctor"
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

# ── Prerequisite check ───────────────────────────────────────────────────────

check_prereq() {
  local name=$1 cmd=$2 version_flag=${3:---version} min_version=${4:-}
  if command -v "$cmd" > /dev/null 2>&1; then
    local ver; ver=$("$cmd" $version_flag 2>&1 | head -1)
    printf "  ✓ %-12s %s\n" "$name" "$ver"
    return 0
  else
    printf "  ✗ %-12s not found\n" "$name"
    return 1
  fi
}

check_prereqs() {
  echo "Prerequisites:"
  local ok=true
  check_prereq "java" java -version || ok=false
  check_prereq "maven" mvn --version || ok=false
  check_prereq "git" git --version || ok=false
  local node_ok=true yarn_ok=true
  check_prereq "node" node --version || node_ok=false
  check_prereq "yarn" yarn --version || yarn_ok=false
  if [ "$node_ok" = false ] || [ "$yarn_ok" = false ]; then
    echo "  ⚠ node/yarn missing — pages and casehub-mosaic will be skipped"
  fi
  echo ""
  if [ "$ok" = false ]; then
    echo "ERROR: required prerequisites missing. Install java, maven, and git."
    exit 1
  fi
}

# ── Help ─────────────────────────────────────────────────────────────────────

show_help() {
  cat <<'HELP'
Usage: ./build-all.sh [OPTIONS] [-- MAVEN_ARGS...]

Clones all casehubio repos (or updates existing), then builds the full
ecosystem in dependency order. Incremental by default — only rebuilds
repos whose HEAD changed since the last successful run.

Modes:
  (default)          Incremental — clone/update, detect changes, build changed
  --aggregate        Single Maven reactor via aggregator.xml (fastest for clean setup)
  --no-cache         Ignore incremental cache, rebuild everything
  --local            Build from current checkout (no git fetch/reset)

Options:
  --skip-tests       Pass -DskipTests to Maven
  --head             Clone/checkout HEAD of each repo (default: verified SHAs from casehub-all)
  --help, -h         Show this help and check prerequisites

Extra Maven args can be passed directly:
  ./build-all.sh --skip-tests -T 1C
HELP
  echo ""
  check_prereqs
  exit 0
}

# Parse flags
NO_CACHE=false
SKIP_TESTS=false
LOCAL=false
AGGREGATE=false
MVN_ARGS=()
for arg in "$@"; do
  case "$arg" in
    --help|-h)       ;; # handled by early check above
    --no-cache)      NO_CACHE=true ;;
    --skip-tests)    SKIP_TESTS=true; MVN_ARGS+=("-DskipTests") ;;
    --local)         LOCAL=true ;;
    --aggregate)     AGGREGATE=true ;;
    --head)          USE_HEAD=true ;;
    *)               MVN_ARGS+=("$arg") ;;
  esac
done

if [ "${SHOW_HELP:-}" = true ]; then
  show_help
fi

check_prereqs

load_csv "$SCRIPT_DIR/build/modules-core.csv"
load_csv "$SCRIPT_DIR/build/modules-applications.csv"

# ── Helpers ──────────────────────────────────────────────────────────────────

local_path() {
  local name=$1
  echo "${PATH_OVERRIDE[$name]:-../$name}"
}

git_path() {
  local name=$1
  echo "${GIT_PATH_OVERRIDE[$name]:-$(local_path "$name")}"
}

gh_repo() {
  local name=$1
  local org="${ORG_OVERRIDE[$name]:-casehubio}"
  local repo="${REPO_OVERRIDE[$name]:-$name}"
  echo "$org/$repo"
}

# ── Setup ────────────────────────────────────────────────────────────────────

mkdir -p "$LOG_DIR"

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

# Auto-detect isx container — default to --local mode
if [ -n "${ISX_CONTAINER:-}" ] && [ "$LOCAL" = false ]; then
  LOCAL=true
fi

# ── Fetch verified SHAs from casehub-all (if --verified) ─────────────────────
declare -A VERIFIED_SHA
if [ "${USE_HEAD:-false}" != true ]; then
  echo ""; echo "==> Fetching verified SHAs from casehub-all (use --head to skip)..."
  CASEHUB_ALL_SHAS=$(git ls-remote --refs https://github.com/casehubio/casehub-all.git HEAD 2>/dev/null | head -1 | cut -f1)
  if [ -n "$CASEHUB_ALL_SHAS" ]; then
    while IFS= read -r line; do
      sha="${line%% *}"
      path="${line##* }"
      path="${path#160000 }"
      # git ls-tree format: mode type sha\tpath
      repo_name="$(basename "$path")"
      VERIFIED_SHA[$repo_name]=$sha
    done < <(git ls-tree "https://github.com/casehubio/casehub-all.git" HEAD 2>/dev/null || git archive --remote=https://github.com/casehubio/casehub-all.git HEAD .gitmodules 2>/dev/null | tar -xO 2>/dev/null | grep "path = " | sed 's/.*path = //' || true)
  fi
  # Simpler approach: clone casehub-all sparsely for submodule SHAs
  if [ ${#VERIFIED_SHA[@]} -eq 0 ]; then
    TMPDIR=$(mktemp -d)
    git clone --depth=1 --filter=blob:none --no-checkout https://github.com/casehubio/casehub-all.git "$TMPDIR/casehub-all" 2>/dev/null
    if [ -d "$TMPDIR/casehub-all" ]; then
      while IFS=$'\t' read -r info path; do
        sha=$(echo "$info" | awk '{print $3}')
        repo_name="$(basename "$path")"
        VERIFIED_SHA[$repo_name]=$sha
        printf "    %-30s %s\n" "$repo_name" "$sha"
      done < <(git -C "$TMPDIR/casehub-all" ls-tree HEAD | grep "^160000")
    fi
    rm -rf "$TMPDIR"
  fi
  echo "    ${#VERIFIED_SHA[@]} verified SHAs loaded"
fi

# ── Step 1: Clone or update ──────────────────────────────────────────────────
if [ "$LOCAL" = true ]; then
  echo ""; echo "==> Local mode: building from current checkout"
  for repo in "${REPOS[@]}"; do
    gdir="$(git_path "$repo")"
    if [ ! -d "$gdir/.git" ]; then
      echo "    ERROR: $repo not found at $gdir"
      exit 1
    fi
  done
else
  echo ""; echo "==> Fetching repos..."
  for repo in "${REPOS[@]}"; do
    gdir="$(git_path "$repo")"
    if [ -d "$gdir/.git" ]; then
      printf "    %-30s updating\n" "$repo"
      git -C "$gdir" fetch --quiet origin main
      local target_sha="${VERIFIED_SHA[$repo]:-origin/main}"
      git -C "$gdir" checkout --quiet "$target_sha" 2>/dev/null || git -C "$gdir" reset --quiet --hard origin/main
    else
      gh_url="https://github.com/$(gh_repo "$repo").git"
      printf "    %-30s cloning into %s\n" "$repo" "$gdir"
      mkdir -p "$(dirname "$gdir")"
      git clone --quiet "$gh_url" "$gdir"
      local target_sha="${VERIFIED_SHA[$repo]:-}"
      if [ -n "$target_sha" ]; then
        git -C "$gdir" checkout --quiet "$target_sha" 2>/dev/null || true
      fi
    fi
  done
fi

# ── Aggregate mode: single Maven reactor, skip incremental analysis ──────────
if [ "$AGGREGATE" = true ]; then
  echo ""; echo "==> Aggregate mode: single Maven reactor"
  echo "==> Installing parent POM..."
  mvn install -N -f "$SCRIPT_DIR/pom.xml" "${MVN_ARGS[@]}"

  if command -v yarn > /dev/null 2>&1; then
    for yarn_repo in pages casehub-mosaic; do
      local_dir="$(local_path "$yarn_repo")"
      if [ -d "$local_dir" ]; then
        echo ""; echo "==> Building $yarn_repo (yarn)"
        (cd "$local_dir" && yarn install && yarn build) || echo "  ⚠ $yarn_repo yarn build failed (continuing)"
      fi
    done
  fi

  echo ""; echo "==> Installing (full reactor)"
  mvn install -fae -f "$SCRIPT_DIR/aggregator.xml" "${MVN_ARGS[@]}"
  echo ""; echo "==> Done (aggregate mode)."
  exit $?
fi

# ── Step 2: Record SHAs (in memory — written to disk only after successful build)
echo ""; echo "==> Recording SHAs..."
declare -A CURR_SHA
for repo in "${REPOS[@]}"; do
  sha=$(git -C "$(git_path "$repo")" rev-parse HEAD)
  CURR_SHA[$repo]=$sha
  printf "    %-30s %s\n" "$repo" "$sha"
done

# ── Step 3: Classify ─────────────────────────────────────────────────────────
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
# Install parent POM first — modules reference it as their parent/import POM,
# and Maven must resolve it locally before the aggregator can parse their POMs.
echo ""; echo "==> Installing parent POM..."
mvn install -N -f "$SCRIPT_DIR/pom.xml" "${MVN_ARGS[@]}"

# pages and casehub-mosaic are yarn-only — not in aggregator.xml
if command -v yarn > /dev/null 2>&1; then
  if [ "${STATE[pages]:-skip}" = "build" ]; then
    echo ""; echo "==> Building pages (yarn)"
    (cd "$(local_path pages)" && yarn install && yarn build) || echo "  ⚠ pages yarn build failed (continuing)"
  fi
  if [ "${STATE[casehub-mosaic]:-skip}" = "build" ]; then
    echo ""; echo "==> Building casehub-mosaic (yarn)"
    (cd "$(local_path casehub-mosaic)" && yarn install && yarn build) || echo "  ⚠ casehub-mosaic yarn build failed (continuing)"
  fi
else
  echo "  ⚠ yarn not found — skipping pages and casehub-mosaic frontend builds"
fi

BUILD_LIST=""
SKIP_COUNT=0
for repo in "${REPOS[@]}"; do
  [ "$repo" = "pages" ] && continue
  [ "$repo" = "casehub-mosaic" ] && continue
  if [ "${STATE[$repo]:-skip}" = "build" ]; then
    BUILD_LIST="${BUILD_LIST:+$BUILD_LIST,}$(local_path "$repo")"
  elif [ "${STATE[$repo]:-skip}" = "skip" ]; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
  fi
done
echo ""
BUILD_EXIT=0
if [ -n "$BUILD_LIST" ]; then
  if [ "$SKIP_COUNT" -gt 0 ]; then
    echo "==> Installing (incremental): $BUILD_LIST"
    mvn install -fae -f "$SCRIPT_DIR/aggregator.xml" -pl "$BUILD_LIST" "${MVN_ARGS[@]}" || BUILD_EXIT=$?
  else
    echo "==> Installing (full reactor)"
    mvn install -fae -f "$SCRIPT_DIR/aggregator.xml" "${MVN_ARGS[@]}" || BUILD_EXIT=$?
  fi
else
  echo "==> Nothing to build."
fi

# ── Step 6: Test ─────────────────────────────────────────────────────────────
TEST_EXIT=0
TEST_LIST=""
for repo in "${REPOS[@]}"; do
  [ "$repo" = "pages" ] && continue
  [ "$repo" = "casehub-mosaic" ] && continue
  [ "${STATE[$repo]:-skip}" = "test" ] && TEST_LIST="${TEST_LIST:+$TEST_LIST,}$(local_path "$repo")"
done
if [ -n "$TEST_LIST" ] && [ "$SKIP_TESTS" = false ]; then
  echo ""; echo "==> Retesting: $TEST_LIST"
  mvn test -fae -f "$SCRIPT_DIR/aggregator.xml" -pl "$TEST_LIST" "${MVN_ARGS[@]}" || TEST_EXIT=$?
fi

# ── Result ───────────────────────────────────────────────────────────────────
if [ "$BUILD_EXIT" -ne 0 ] || [ "$TEST_EXIT" -ne 0 ]; then
  echo ""
  echo "==> BUILD FAILED — some modules had errors."
  echo "  Review the output above for FAILURE lines."
  echo "  To resume from a failed module:"
  echo "    mvn install -fae -f aggregator.xml -rf :<failed-module> ${MVN_ARGS[*]}"
  echo ""
  echo "  SHA log NOT written — next run will rebuild all changed modules."
  exit 1
fi

# ── Write SHA log (only on success) ──────────────────────────────────────────
{ echo "# casehubio full-stack build"; echo "# timestamp: $TIMESTAMP"; echo ""; } > "$LOG_FILE"
for repo in "${REPOS[@]}"; do
  echo "$repo=${CURR_SHA[$repo]}" >> "$LOG_FILE"
done

echo ""
echo "==> Done. SHA log: $LOG_FILE"
