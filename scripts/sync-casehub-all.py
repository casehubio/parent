#!/usr/bin/env python3
"""
Dispatch ecosystem-build-succeeded to casehub-all with the current build SHAs.

Reads:
  build/modules-core.csv         — core module names
  build/modules-applications.csv — application module names
  .build-shas/<name>             — SHA written by the Collect SHAs step

Environment:
  GH_TOKEN          — PAT with repo scope (for cross-repo dispatch)
  INCLUDE_APPLICATIONS — "true" to include application module SHAs
  TRIGGER           — event name (defaults to "workflow_dispatch")
"""

import json, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(name):
    try:
        return (ROOT / '.build-shas' / name).read_text().strip()
    except Exception:
        return ''


def load_csv(path):
    names = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        names.append(line.split(',')[0])
    return names


include_apps = os.environ.get('INCLUDE_APPLICATIONS', 'false') == 'true'
core = load_csv(ROOT / 'build' / 'modules-core.csv')
apps = load_csv(ROOT / 'build' / 'modules-applications.csv') if include_apps else []

shas = {'parent': sha('parent')}
for name in core + apps:
    shas[name.replace('-', '_')] = sha(name)

# GitHub repository dispatch limits client_payload to 10 top-level properties.
# Nest all SHAs under a single 'shas' key to stay within the limit.
payload = {
    'event_type': 'ecosystem-build-succeeded',
    'client_payload': {
        'trigger': os.environ.get('TRIGGER', 'workflow_dispatch'),
        'shas': shas,
    }
}

subprocess.run(
    ['gh', 'api', 'repos/casehubio/casehub-all/dispatches', '--input', '-'],
    input=json.dumps(payload).encode(),
    check=True,
    env=os.environ.copy()
)
print('casehub-all dispatch sent — SHAs from .build-shas/')
