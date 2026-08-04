#!/bin/bash
set -euo pipefail

# Sync docs/guides/ from each child repo into parent docs/repos/ via git
# subtree split + merge.
#
# Same pattern as casehub-examples/sync.sh — subtree split isolates the
# docs/guides/ directory, subtree add/pull merges it into a prefix.
#
# Usage:
#   scripts/sync-guides.sh              # sync all repos
#   scripts/sync-guides.sh --repo work  # sync single repo
#   scripts/sync-guides.sh --check      # dry-run — report stale prefixes
#   scripts/sync-guides.sh --local      # use sibling clones instead of GitHub

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG="$SCRIPT_DIR/guide-sync-config.json"
TMPDIR=$(mktemp -d)

trap 'rm -rf "$TMPDIR"' EXIT

CHECK_ONLY=false
LOCAL_MODE=false
SINGLE_REPO=""

for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=true ;;
    --local) LOCAL_MODE=true ;;
    --repo)  shift_next=true ;;
    *)
      if [ "${shift_next:-}" = "true" ]; then
        SINGLE_REPO="$arg"
        shift_next=false
      fi
      ;;
  esac
done

# Re-parse --repo since the above loop is fragile with shift
for i in $(seq 1 $#); do
  arg="${!i}"
  if [ "$arg" = "--repo" ]; then
    next=$((i + 1))
    SINGLE_REPO="${!next}"
  fi
done

synced=0
skipped=0
failed=0

python3 -c "
import json, sys
config = json.load(open('$CONFIG'))
for r in config['repos']:
    repo = r.get('repo', r['name'])
    target = r.get('target_base', 'casehub-' + r['name'])
    print(f\"{r['name']} {r['org']} {repo} {target}\")
" | while read -r name org repo target; do

  if [ -n "$SINGLE_REPO" ] && [ "$name" != "$SINGLE_REPO" ]; then
    continue
  fi

  prefix="docs/repos/$target"

  if $LOCAL_MODE; then
    clone_dir="$PARENT_DIR/../$name"
    if [ ! -d "$clone_dir/.git" ]; then
      echo "  SKIP $name: ../$name/ not a git repo"
      continue
    fi
  else
    repo_url="https://github.com/$org/$repo.git"
    clone_dir="$TMPDIR/$name"
    git clone --quiet --depth=1 "$repo_url" "$clone_dir" 2>/dev/null || {
      echo "  SKIP $name: could not clone $repo_url"
      continue
    }
  fi

  if [ ! -f "$clone_dir/docs/guides/consumer-guide.md" ] && [ ! -f "$clone_dir/docs/guides/contributor-guide.md" ] && [ ! -d "$clone_dir/docs/guides/api" ]; then
    echo "  SKIP $name: no docs/guides/ content (consumer-guide.md, contributor-guide.md, or api/)"
    [ ! $LOCAL_MODE ] && rm -rf "$clone_dir"
    continue
  fi

  if $CHECK_ONLY; then
    if [ -d "$PARENT_DIR/$prefix" ]; then
      echo "  CURRENT $name ($prefix/)"
    else
      echo "  MISSING $name ($prefix/ not yet seeded)"
    fi
    [ ! $LOCAL_MODE ] && rm -rf "$clone_dir"
    continue
  fi

  # Subtree split: isolate docs/ into a synthetic branch
  split_dir="$clone_dir"
  if $LOCAL_MODE; then
    # For local repos, clone to temp first to avoid modifying the working repo
    split_dir="$TMPDIR/$name-split"
    git clone --quiet "$clone_dir" "$split_dir" 2>/dev/null
  fi

  (cd "$split_dir" && git subtree split --prefix=docs/guides -b docs-guides --quiet 2>/dev/null) || {
    echo "  SKIP $name: subtree split failed"
    rm -rf "$split_dir"
    continue
  }

  if [ -d "$PARENT_DIR/$prefix" ]; then
    git -C "$PARENT_DIR" subtree pull --prefix="$prefix" "$split_dir" docs-guides --squash \
      -m "docs(#377): sync $name guides via subtree" --quiet 2>/dev/null || {
      echo "  WARN $name: subtree pull failed (may need manual merge)"
      rm -rf "$split_dir"
      continue
    }
    echo "  UPDATED $name → $prefix/"
  else
    git -C "$PARENT_DIR" subtree add --prefix="$prefix" "$split_dir" docs-guides --squash \
      -m "docs(#377): seed $name guides via subtree" --quiet 2>/dev/null || {
      echo "  WARN $name: subtree add failed"
      rm -rf "$split_dir"
      continue
    }
    echo "  SEEDED $name → $prefix/"
  fi

  [ "$split_dir" != "$clone_dir" ] && rm -rf "$split_dir"
  [ ! $LOCAL_MODE ] && rm -rf "$clone_dir"

done

echo ""
echo "Sync complete."
