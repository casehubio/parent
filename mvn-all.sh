#!/usr/bin/env bash
# mvn-all.sh — Full-stack Maven reactor build via aggregator.xml
#
# Builds all Maven modules in a single reactor. Does NOT handle
# yarn-only modules (pages, casehub-mosaic) — use build-all.sh for those.
#
# Usage:
#   ./mvn-all.sh                     # build all
#   ./mvn-all.sh -DskipTests         # skip tests
#   ./mvn-all.sh -T 1C               # parallel build
#   ./mvn-all.sh -Plangchain4j       # include quarkus-langchain4j
#   ./mvn-all.sh -pl ../engine       # build a single module + deps
#
# All args are passed directly to mvn.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing parent POM..."
mvn install -N -f "$SCRIPT_DIR/pom.xml" -q

echo "==> Building reactor..."
mvn install -fae -f "$SCRIPT_DIR/aggregator.xml" "$@"
