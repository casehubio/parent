#!/bin/bash
set -euo pipefail

# Generate API documentation for a repo's -api module using jmarkdoc.
#
# Usage:
#   scripts/generate-api-docs.sh <repo-root> [<api-source-dir>]
#
# Defaults:
#   api-source-dir: api/src/main/java (standard -api module layout)
#
# Requires: JDK 25+ on PATH (or JAVA_HOME pointing to one).
# Downloads jmarkdoc.jar on first run (cached in .build/).
#
# Output: docs/guides/api/ in the repo root (clean-slate regeneration).
# Exit code: 0 if docs changed, 1 if no change (for CI diff-gating).

REPO_ROOT="${1:?Usage: generate-api-docs.sh <repo-root> [<api-source-dir>]}"
API_SRC="${2:-api/src/main/java}"

JMARKDOC_JAR="$REPO_ROOT/.build/jmarkdoc.jar"
JMARKDOC_URL="https://github.com/AdamBien/jMarkDoc/releases/latest/download/jmarkdoc.jar"
OUTPUT_DIR="$REPO_ROOT/docs/guides/api"

# Resolve JAVA_HOME for JDK 25+
if [ -z "${JAVA_HOME:-}" ]; then
  for jdk in /Library/Java/JavaVirtualMachines/jdk-2[5-9].jdk/Contents/Home /Library/Java/JavaVirtualMachines/jdk-3*.jdk/Contents/Home; do
    if [ -d "$jdk" ]; then
      JAVA_HOME="$jdk"
      break
    fi
  done
fi

JAVA="${JAVA_HOME:?No JDK 25+ found. Set JAVA_HOME.}/bin/java"

# Verify JDK version
JDK_VERSION=$("$JAVA" -version 2>&1 | head -1 | grep -oE '"[0-9]+' | tr -d '"')
if [ "$JDK_VERSION" -lt 25 ] 2>/dev/null; then
  echo "Error: JDK 25+ required (found $JDK_VERSION). Set JAVA_HOME to a JDK 25+ installation."
  exit 2
fi

# Download jmarkdoc if not cached
if [ ! -f "$JMARKDOC_JAR" ]; then
  mkdir -p "$(dirname "$JMARKDOC_JAR")"
  echo "Downloading jmarkdoc.jar..."
  curl -fsSL "$JMARKDOC_URL" -o "$JMARKDOC_JAR"
fi

# Resolve source directory
SRC_DIR="$REPO_ROOT/$API_SRC"
if [ ! -d "$SRC_DIR" ]; then
  echo "Error: source directory not found: $SRC_DIR"
  exit 2
fi

# Clean slate
rm -rf "$OUTPUT_DIR"

# Generate
"$JAVA" -jar "$JMARKDOC_JAR" "$SRC_DIR" "$OUTPUT_DIR" 2>&1

# Report
COUNT=$(find "$OUTPUT_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "Generated $COUNT types in $OUTPUT_DIR"

# Exit code for CI: 0 = changed (needs commit), 1 = no change
if git -C "$REPO_ROOT" diff --quiet -- docs/guides/api/ 2>/dev/null; then
  if git -C "$REPO_ROOT" ls-files --others -- docs/guides/api/ | grep -q .; then
    exit 0  # new untracked files = change
  fi
  echo "No changes detected."
  exit 1
fi
exit 0
