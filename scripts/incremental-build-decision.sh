#!/usr/bin/env bash
# incremental-build-decision.sh
#
# Determines the BUILD/TEST/SKIP decision for one module in the incremental
# full-stack build, based on SHA comparisons between the current run and the
# last successful build.
#
# Usage:
#   incremental-build-decision.sh \
#     --module <name> \
#     --current-sha <sha> \
#     --previous-sha <sha|"none"> \
#     --dep <name>:<current-sha>:<previous-sha> \
#     [--dep <name>:<current-sha>:<previous-sha> ...]
#
# Output (stdout): one of BUILD, TEST, SKIP
# Exit code: always 0
#
# Logic (evaluated in priority order):
#   1. previous-sha == "none"         → BUILD  (first run, no cache)
#   2. current-sha != previous-sha    → BUILD  (own source changed)
#   3. any dep current != previous    → TEST   (dep changed, source intact)
#   4. all SHAs match                 → SKIP

set -euo pipefail

MODULE=""
CURRENT_SHA=""
PREVIOUS_SHA=""
declare -a DEPS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --module)       MODULE="$2";       shift 2 ;;
    --current-sha)  CURRENT_SHA="$2";  shift 2 ;;
    --previous-sha) PREVIOUS_SHA="$2"; shift 2 ;;
    --dep)          DEPS+=("$2");      shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$MODULE" || -z "$CURRENT_SHA" || -z "$PREVIOUS_SHA" ]]; then
  echo "Usage: $0 --module <name> --current-sha <sha> --previous-sha <sha|none> [--dep name:cur:prev ...]" >&2
  exit 1
fi

# Rule 1: no previous state → BUILD
if [[ "$PREVIOUS_SHA" == "none" ]]; then
  echo "BUILD"
  exit 0
fi

# Rule 2: own source changed → BUILD
if [[ "$CURRENT_SHA" != "$PREVIOUS_SHA" ]]; then
  echo "BUILD"
  exit 0
fi

# Rule 3: any transitive dep changed → TEST
for dep in "${DEPS[@]:-}"; do
  dep_current="${dep#*:}"
  dep_current="${dep_current%:*}"
  dep_previous="${dep##*:}"
  if [[ "$dep_current" != "$dep_previous" ]]; then
    echo "TEST"
    exit 0
  fi
done

# Rule 4: nothing changed → SKIP
echo "SKIP"
exit 0
