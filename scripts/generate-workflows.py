#!/usr/bin/env python3
"""
Generate the build step blocks in both workflow files from build/modules-*.csv.
Run via pre-commit hook when a CSV changes, or manually:
  python3 scripts/generate-workflows.py

Rewrites only the sections between:
  # -- BEGIN GENERATED
  # -- END GENERATED
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CORE_CSV  = ROOT / 'build' / 'modules-core.csv'
APP_CSV   = ROOT / 'build' / 'modules-applications.csv'
FULL_YML  = ROOT / '.github' / 'workflows' / 'full-stack-build.yml'
INCR_YML  = ROOT / '.github' / 'workflows' / 'incremental-full-stack-build.yml'

BEGIN = '      # -- BEGIN GENERATED'
END   = '      # -- END GENERATED'

# Repos that deviate from casehubio/<name>
REPO_OVERRIDE = {'pages': 'casehubio/casehub-pages'}
# Repos that need GH_PAT instead of GITHUB_TOKEN
PRIVATE = {'quarkmind', 'flow'}
# Repos with a build subdir
SUBDIR = {'drafthouse': 'server'}
# Repos using yarn instead of maven
YARN = {'pages'}


def load_csv(path):
    modules = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(',')
        modules.append({'name': parts[0], 'deps': parts[1:]})
    return modules


def sha_output(name):
    return 'sha_' + name.replace('-', '_')


def dep_env_key(name):
    return name.upper().replace('-', '_')


# ── full-stack-build.yml ──────────────────────────────────────────────────────

def full_step(mod, tier):
    name  = mod['name']
    sub   = SUBDIR.get(name, '')
    cd    = 'casehub/' + name + ('/' + sub if sub else '')
    depth = '../../' + ('../' if sub else '')

    lines = []
    lines.append('')
    if tier == 'application':
        lines.append('      - name: "Build: ' + name + '"')
        lines.append('        if: inputs.include_applications')
    else:
        lines.append('      - name: "Build: ' + name + '"')
    lines.append('        id: ' + name)
    lines.append('        continue-on-error: true')
    lines.append('        env:')

    if name in YARN:
        lines.append('          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}')
    else:
        lines.append('          SKIP_TESTS: ${{ inputs.skip_tests }}')
        lines.append('          SKIP_ITS: ${{ inputs.skip_integration_tests }}')
        lines.append('          MAVEN_EXTRA: ${{ inputs.maven_args }}')
        lines.append('          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}')
    if name in PRIVATE:
        lines.append('          GH_TOKEN: ${{ secrets.GH_PAT }}')

    lines.append('        run: |')
    lines.append('          mkdir -p .build-outcomes')

    if name in YARN:
        lines.append('          START=$SECONDS')
        lines.append('          if cd ' + cd + ' && yarn install && yarn build; then')
        lines.append('            echo "success" > ' + depth + '.build-outcomes/' + name)
        lines.append('          else')
        lines.append('            echo "failure" > ' + depth + '.build-outcomes/' + name)
        lines.append('          fi')
    else:
        lines.append('          FLAGS=""')
        lines.append('          [ "$SKIP_TESTS" = "true" ] && FLAGS="-DskipTests"')
        lines.append('          [ "$SKIP_ITS" = "true" ] && FLAGS="$FLAGS -DskipITs"')
        lines.append('          START=$SECONDS')
        lines.append('          if cd ' + cd + ' && mvn install --batch-mode $FLAGS $MAVEN_EXTRA; then')
        lines.append('            echo "success" > ' + depth + '.build-outcomes/' + name)
        lines.append('          else')
        lines.append('            echo "failure" > ' + depth + '.build-outcomes/' + name)
        lines.append('          fi')

    lines.append('          echo $((SECONDS - START)) > ' + depth + '.build-times/' + name)
    return '\n'.join(lines)


def generate_full(core, apps):
    parts = []
    for mod in core:
        parts.append(full_step(mod, 'core'))
    for mod in apps:
        parts.append(full_step(mod, 'application'))
    return '\n'.join(parts) + '\n'


# ── incremental-full-stack-build.yml ─────────────────────────────────────────

def incr_step(mod, tier):
    name  = mod['name']
    deps  = mod['deps']
    sub   = SUBDIR.get(name, '')
    cd    = 'casehub/' + name + ('/' + sub if sub else '')

    lines = []
    lines.append('')
    if tier == 'application':
        lines.append('      - name: "Build: ' + name + '"')
        lines.append('        if: inputs.include_applications')
    else:
        lines.append('      - name: "Build: ' + name + '"')
    lines.append('        id: ' + name)
    lines.append('        continue-on-error: true')
    lines.append('        env:')
    lines.append('          CUR: ${{ steps.shas.outputs.' + sha_output(name) + ' }}')
    lines.append('          PRV: ${{ steps.prev.outputs.' + sha_output(name) + ' }}')

    for dep in deps:
        k = dep_env_key(dep)
        lines.append('          CUR_' + k + ': ${{ steps.shas.outputs.' + sha_output(dep) + ' }}')
        lines.append('          PRV_' + k + ': ${{ steps.prev.outputs.' + sha_output(dep) + ' }}')

    if name not in YARN:
        lines.append('          SKIP_TESTS: ${{ inputs.skip_tests }}')
        lines.append('          SKIP_ITS: ${{ inputs.skip_integration_tests }}')
        lines.append('          MAVEN_EXTRA: ${{ inputs.maven_args }}')
    lines.append('          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}')
    if name in PRIVATE:
        lines.append('          GH_TOKEN: ${{ secrets.GH_PAT }}')

    lines.append('        run: |')
    lines.append('          mkdir -p .build-outcomes .build-decisions')

    # Decision script call
    decision = ('          D=$(./scripts/incremental-build-decision.sh \\\n'
                '            --module ' + name + ' --current-sha "$CUR" --previous-sha "${PRV:-none}"')
    for dep in deps:
        k = dep_env_key(dep)
        decision += ' \\\n            --dep "' + dep + ':${CUR_' + k + '}:${PRV_' + k + ':-none}"'
    decision += ')'
    lines.append(decision)
    lines.append('          echo "decision=$D" >> $GITHUB_OUTPUT')
    lines.append('          echo "$D" > .build-decisions/' + name)
    lines.append('          START=$SECONDS')
    lines.append('          RC=0')

    if name in YARN:
        lines.append('          case "$D" in')
        lines.append('            SKIP) echo "⏭️  ' + name + ': SKIP" ;;')
        lines.append('            TEST) echo "⏭️  ' + name + ': SKIP (yarn-only, no separate test phase)" ;;')
        lines.append('            BUILD) cd ' + cd + ' && yarn install && yarn build || RC=$? ;;')
        lines.append('          esac')
    else:
        lines.append('          case "$D" in')
        lines.append('            SKIP) echo "⏭️  ' + name + ': SKIP" ;;')
        lines.append('            TEST)')
        lines.append('              if [ "$SKIP_TESTS" = "true" ]; then echo "⏭️  ' + name + ': SKIP (TEST — tests disabled)"')
        lines.append('              else')
        lines.append('                ITS=""; [ "$SKIP_ITS" = "true" ] && ITS="-DskipITs"')
        lines.append('                cd ' + cd + ' && mvn test --batch-mode $ITS $MAVEN_EXTRA || RC=$?')
        lines.append('              fi ;;')
        lines.append('            BUILD)')
        lines.append('              F=""; [ "$SKIP_TESTS" = "true" ] && F="-DskipTests"')
        lines.append('              [ "$SKIP_ITS" = "true" ] && F="$F -DskipITs"')
        lines.append('              cd ' + cd + ' && mvn install --batch-mode $F $MAVEN_EXTRA || RC=$? ;;')
        lines.append('          esac')

    lines.append('          [ $RC -eq 0 ] && echo "success" > .build-outcomes/' + name + ' || echo "failure" > .build-outcomes/' + name)
    lines.append('          echo $((SECONDS - START)) > .build-times/' + name)
    return '\n'.join(lines)


def generate_incr(core, apps):
    parts = []
    for mod in core:
        parts.append(incr_step(mod, 'core'))
    for mod in apps:
        parts.append(incr_step(mod, 'application'))
    return '\n'.join(parts) + '\n'


# ── File rewriter ─────────────────────────────────────────────────────────────

def rewrite(path, generated):
    text = path.read_text()
    before = text.find(BEGIN)
    after  = text.find(END)
    if before == -1 or after == -1:
        print(f'ERROR: markers not found in {path}', file=sys.stderr)
        sys.exit(1)
    after_end = after + len(END)
    new_text = (text[:before]
                + BEGIN + '\n'
                + generated
                + END
                + text[after_end:])
    if new_text == text:
        print(f'  {path.name}: unchanged')
        return False
    path.write_text(new_text)
    print(f'  {path.name}: updated')
    return True


def main():
    core = load_csv(CORE_CSV)
    apps = load_csv(APP_CSV)

    changed = False
    changed |= rewrite(FULL_YML, generate_full(core, apps))
    changed |= rewrite(INCR_YML, generate_incr(core, apps))

    if changed:
        print('Workflow files updated — stage them before committing.')
    else:
        print('Nothing changed.')


if __name__ == '__main__':
    main()
