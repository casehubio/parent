#!/usr/bin/env bash
# Install git hooks for this repo. Run once after cloning.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK="$HOOKS_DIR/pre-commit"

cat > "$HOOK" << 'HOOK_BODY'
#!/usr/bin/env bash
# Regenerate workflow build steps if any modules CSV changed.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Check if either CSV is staged
if git diff --cached --name-only | grep -qE '^build/modules-(core|applications)\.csv$'; then
  echo "build/modules-*.csv changed — regenerating workflow build steps..."
  python3 "$REPO_ROOT/scripts/generate-workflows.py"
  git add \
    "$REPO_ROOT/.github/workflows/full-stack-build.yml" \
    "$REPO_ROOT/.github/workflows/incremental-full-stack-build.yml"
  echo "Workflow files updated and staged."
fi
HOOK_BODY

chmod +x "$HOOK"
echo "pre-commit hook installed at $HOOK"
