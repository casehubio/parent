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
# Directory layout:
#   ~/claude/casehub/parent/   ← this script lives here
#   ~/claude/casehub/ledger/   ← sibling repos one level up inside casehub/
#   ~/claude/casehub/work/
#   ~/claude/quarkus-langchain4j/  ← outside casehub/
#
# Usage:
#   ./build-all.sh                  # incremental build
#   ./build-all.sh --no-cache       # force full rebuild
#   ./build-all.sh --skip-tests
#   ./build-all.sh -DskipTests
#   ./build-all.sh -T 1C
#   ./build-all.sh --include-apps   # also build devtown, aml, clinical

set -euo pipefail

ORG="casehubio"
BRANCH="main"
LOG_DIR="build-logs"
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
LOG_FILE="$LOG_DIR/$TIMESTAMP.shas"

# Repo name → local directory (relative to this script)
declare -A REPO_DIR
REPO_DIR[quarkus-langchain4j]="../../quarkus-langchain4j"
REPO_DIR[platform]="../platform"
REPO_DIR[ledger]="../ledger"
REPO_DIR[eidos]="../eidos"
REPO_DIR[connectors]="../connectors"
REPO_DIR[work]="../work"
REPO_DIR[qhorus]="../qhorus"
REPO_DIR[engine]="../engine"
REPO_DIR[workers]="../workers"
REPO_DIR[claudony]="../claudony"
REPO_DIR[openclaw]="../openclaw"
REPO_DIR[devtown]="../devtown"
REPO_DIR[aml]="../aml"
REPO_DIR[clinical]="../clinical"
REPO_DIR[life]="../life"
REPO_DIR[drafthouse]="../drafthouse/server"

# Repo name → GitHub repo name (for cloning)
declare -A REPO_GH
REPO_GH[quarkus-langchain4j]="quarkus-langchain4j"
REPO_GH[platform]="platform"
REPO_GH[ledger]="ledger"
REPO_GH[eidos]="eidos"
REPO_GH[connectors]="connectors"
REPO_GH[work]="work"
REPO_GH[qhorus]="qhorus"
REPO_GH[engine]="engine"
REPO_GH[workers]="workers"
REPO_GH[claudony]="claudony"
REPO_GH[openclaw]="openclaw"
REPO_GH[devtown]="devtown"
REPO_GH[aml]="aml"
REPO_GH[clinical]="clinical"
REPO_GH[life]="life"
REPO_GH[drafthouse]="drafthouse"

# Dependency graph
declare -A DEPS
DEPS[quarkus-langchain4j]=""
DEPS[platform]=""
DEPS[ledger]="platform"
DEPS[eidos]="ledger"
DEPS[connectors]="platform"
DEPS[work]="ledger connectors"
DEPS[qhorus]="ledger work"
DEPS[engine]="quarkus-langchain4j ledger work"
DEPS[workers]="platform engine"
DEPS[claudony]="ledger work qhorus"
DEPS[openclaw]="platform ledger qhorus engine"
DEPS[devtown]="ledger work qhorus engine"
DEPS[aml]="ledger work qhorus engine"
DEPS[clinical]="ledger work qhorus engine"
DEPS[life]="ledger work qhorus engine openclaw"
DEPS[drafthouse]="qhorus"

# Core build order (topological) — apps added below if --include-apps
REPOS=(quarkus-langchain4j platform ledger eidos connectors work qhorus engine workers claudony)

# Aggregator module paths (match aggregator.xml <module> entries)
declare -A MODULE_PATH
MODULE_PATH[quarkus-langchain4j]="../../quarkus-langchain4j"
MODULE_PATH[platform]="../platform"
MODULE_PATH[ledger]="../ledger"
MODULE_PATH[eidos]="../eidos"
MODULE_PATH[connectors]="../connectors"
MODULE_PATH[work]="../work"
MODULE_PATH[qhorus]="../qhorus"
MODULE_PATH[engine]="../engine"
MODULE_PATH[workers]="../workers"
MODULE_PATH[claudony]="../claudony"
MODULE_PATH[openclaw]="../openclaw"
MODULE_PATH[devtown]="../devtown"
MODULE_PATH[aml]="../aml"
MODULE_PATH[clinical]="../clinical"
MODULE_PATH[life]="../life"
MODULE_PATH[drafthouse]="../drafthouse/server"

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

if [ "$INCLUDE_APPS" = true ]; then
  REPOS+=(openclaw devtown aml clinical life drafthouse)
fi

mkdir -p "$LOG_DIR"
{ echo "# casehubio full-stack build"; echo "# timestamp: $TIMESTAMP"; echo ""; } > "$LOG_FILE"

# Load previous cache
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

# Step 1: Clone or update
echo ""; echo "==> Fetching repos..."
for repo in "${REPOS[@]}"; do
  dir="${REPO_DIR[$repo]}"; gh_repo="${REPO_GH[$repo]}"
  if [ -d "$dir/.git" ]; then
    printf "    %-22s updating\n" "$repo"
    git -C "$dir" fetch --quiet origin "$BRANCH"
    git -C "$dir" reset --quiet --hard "origin/$BRANCH"
  else
    printf "    %-22s cloning into %s\n" "$repo" "$dir"
    mkdir -p "$(dirname "$dir")"
    git clone --quiet "https://github.com/$ORG/$gh_repo.git" "$dir"
  fi
done

# Step 2: Record SHAs
echo ""; echo "==> Recording SHAs..."
declare -A CURR_SHA
for repo in "${REPOS[@]}"; do
  sha=$(git -C "${REPO_DIR[$repo]}" rev-parse HEAD)
  CURR_SHA[$repo]=$sha
  echo "$repo=$sha" >> "$LOG_FILE"
  printf "    %-22s %s\n" "$repo" "$sha"
done

# Step 3: Pin to SHAs
for repo in "${REPOS[@]}"; do
  git -C "${REPO_DIR[$repo]}" checkout --quiet --detach "${CURR_SHA[$repo]}"
done

# Step 4: Classify
echo ""; echo "==> Incremental analysis..."
declare -A STATE
for repo in "${REPOS[@]}"; do
  curr="${CURR_SHA[$repo]}"; prev="${PREV_SHA[$repo]:-}"
  if [ "$curr" != "$prev" ] || [ "$NO_CACHE" = true ]; then
    STATE[$repo]=build
    printf "    %-22s BUILD\n" "$repo"
    continue
  fi
  dep_built=false
  for dep in ${DEPS[$repo]}; do
    [ "${STATE[$dep]:-skip}" != "skip" ] && dep_built=true && break
  done
  if [ "$dep_built" = true ]; then
    STATE[$repo]=test; printf "    %-22s TEST\n" "$repo"
  else
    STATE[$repo]=skip; printf "    %-22s SKIP\n" "$repo"
  fi
done

# Step 5: Build
BUILD_LIST=""
for repo in "${REPOS[@]}"; do
  [ "${STATE[$repo]}" = "build" ] && BUILD_LIST="${BUILD_LIST:+$BUILD_LIST,}${MODULE_PATH[$repo]}"
done
echo ""
if [ -n "$BUILD_LIST" ]; then
  echo "==> Installing: $BUILD_LIST"
  mvn install -f aggregator.xml -pl "$BUILD_LIST" "${MVN_ARGS[@]}"
else
  echo "==> Nothing to build."
fi

# Step 6: Test
TEST_LIST=""
for repo in "${REPOS[@]}"; do
  [ "${STATE[$repo]}" = "test" ] && TEST_LIST="${TEST_LIST:+$TEST_LIST,}${MODULE_PATH[$repo]}"
done
if [ -n "$TEST_LIST" ] && [ "$SKIP_TESTS" = false ]; then
  echo ""; echo "==> Retesting: $TEST_LIST"
  mvn test -f aggregator.xml -pl "$TEST_LIST" "${MVN_ARGS[@]}"
fi

echo ""
echo "==> Done. SHA log: $LOG_FILE"
