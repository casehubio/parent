#!/usr/bin/env python3
"""
Dispatch ecosystem-build-succeeded to casehub-all with the current build SHAs.

Works in two modes:
  CI mode   — reads from .build-shas/<name> files written by the Collect SHAs step
  Local mode — falls back to reading git HEAD from sibling repos (../platform etc.)

Usage (local):
  python3 scripts/sync-casehub-all.py
  python3 scripts/sync-casehub-all.py --include-apps

Environment:
  GH_TOKEN             — PAT with repo scope (for cross-repo dispatch)
  INCLUDE_APPLICATIONS — "true" to include application module SHAs
  TRIGGER              — event name (defaults to "local")
"""

import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Local path overrides: name → path relative to parent repo root's parent directory
LOCAL_PATH_OVERRIDE = {
    'pages': '../pages',          # cloned from casehub-pages but lives at ../pages
    'drafthouse': '../drafthouse', # builds from server/ but repo is at ../drafthouse
}


def sha_from_file(name):
    """CI mode: read SHA written by Collect SHAs step."""
    try:
        return (ROOT / '.build-shas' / name).read_text().strip()
    except Exception:
        return None


def sha_from_git(name):
    """Local mode: read HEAD SHA from sibling repo."""
    rel = LOCAL_PATH_OVERRIDE.get(name, f'../{name}')
    repo_path = ROOT / rel
    if not repo_path.exists():
        return None
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception:
        return None


def sha(name):
    """Try CI files first, fall back to local git."""
    return sha_from_file(name) or sha_from_git(name) or ''


def load_csv(path):
    names = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        names.append(line.split(',')[0])
    return names


# Parse --include-apps flag when run directly
include_apps = (
    os.environ.get('INCLUDE_APPLICATIONS', 'false') == 'true'
    or '--include-apps' in sys.argv
)

core = load_csv(ROOT / 'build' / 'modules-core.csv')
apps = load_csv(ROOT / 'build' / 'modules-applications.csv') if include_apps else []

# Parent SHA: CI file first, then local git HEAD of the parent repo itself
parent_sha = sha_from_file('parent') or subprocess.run(
    ['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
    capture_output=True, text=True, check=True
).stdout.strip()

shas = {'parent': parent_sha}
for name in core + apps:
    s = sha(name)
    if s:
        shas[name.replace('-', '_')] = s

mode = 'CI' if (ROOT / '.build-shas').exists() else 'local'
print(f'Syncing casehub-all ({mode} mode) — {len(shas)} SHAs')

# GitHub repository dispatch limits client_payload to 10 top-level properties.
# Nest all SHAs under a single 'shas' key to stay within the limit.
payload = {
    'event_type': 'ecosystem-build-succeeded',
    'client_payload': {
        'trigger': os.environ.get('TRIGGER', 'local'),
        'shas': shas,
    }
}

subprocess.run(
    ['gh', 'api', 'repos/casehubio/casehub-all/dispatches', '--input', '-'],
    input=json.dumps(payload).encode(),
    check=True,
    env=os.environ.copy()
)
print('casehub-all dispatch sent.')

try:
    subprocess.run(
        ['gh', 'api', 'repos/casehubio/examples/dispatches', '--input', '-'],
        input=json.dumps(payload).encode(),
        check=True,
        env=os.environ.copy()
    )
    print('examples dispatch sent.')
except subprocess.CalledProcessError as e:
    print(f'WARNING: examples dispatch failed — {e}')
