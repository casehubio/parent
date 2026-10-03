#!/bin/bash
# Build a single PDF from the brief markdown files.
# Auto-derives anchor IDs from H1 headings — no hardcoded mapping.
#
# Prerequisites: pandoc, weasyprint
#   brew install pandoc weasyprint
#
# Usage:
#   cd parent && bash docs/scripts/build-brief-pdf.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIEF="$SCRIPT_DIR/../brief"
CSS="$SCRIPT_DIR/brief-style.css"
COMBINED="/tmp/casehub-brief-combined.md"
HTML="/tmp/casehub-brief.html"
PDF="$BRIEF/casehub-brief.pdf"

# Pages in reading order
FILES=(
  README.md
  00-positioning.md
  01-declaration-surface.md
  01-yaml-walkthrough.md
  02-agentic-orchestration.md
  03-ai-knowledge-learning.md
  04-enterprise-execution.md
  05-accountability-governance.md
  06-convergence-situational-awareness.md
  07-agent-identity-cognition.md
  08-shared-foundation.md
  09-application-surface.md
  10-applications.md
  23-vision.md
)

# Step 1: Build anchor map from H1 headings (pandoc slug algorithm)
declare -A ANCHORS
for f in "${FILES[@]}"; do
  filepath="$BRIEF/$f"
  if [ ! -f "$filepath" ]; then
    echo "WARNING: $f not found, skipping"
    continue
  fi
  h1=$(grep -m1 "^# " "$filepath" | sed 's/^# //' || true)
  if [ -n "$h1" ]; then
    slug=$(echo "$h1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 -]//g' | tr ' ' '-' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
    ANCHORS["$f"]="#$slug"
  fi
done

# Step 2: Concatenate with page breaks
> "$COMBINED"
for f in "${FILES[@]}"; do
  filepath="$BRIEF/$f"
  [ -f "$filepath" ] || continue
  echo "" >> "$COMBINED"
  cat "$filepath" >> "$COMBINED"
  echo "" >> "$COMBINED"
  echo "---" >> "$COMBINED"
  echo "" >> "$COMBINED"
done

# Step 3: Replace file links with anchor links
for f in "${!ANCHORS[@]}"; do
  anchor="${ANCHORS[$f]}"
  sed -i '' "s|($f)|(${anchor})|g" "$COMBINED"
done

echo "Combined $(wc -l < "$COMBINED" | tr -d ' ') lines"

# Step 4: Markdown → HTML
pandoc "$COMBINED" \
  --from markdown \
  --to html5 \
  --standalone \
  --css "$CSS" \
  --metadata "title=CaseHub — The Accountable AI Harness" \
  --resource-path "$BRIEF" \
  -o "$HTML"

# Step 5: HTML → PDF
weasyprint "$HTML" "$PDF" --base-url "$BRIEF/" 2>&1 | grep -v "^WARNING:" || true

SIZE=$(ls -lh "$PDF" | awk '{print $5}')
echo "Done: $PDF ($SIZE)"
