---
id: PP-20260525-724406
title: "Python components in Maven repos live in python/ with own pyproject.toml — not as Maven modules"
type: rule
scope: platform
applies_to: "Integration-tier repos (casehub-openclaw and any future repos mixing Java and Python)"
severity: guidance
refs:
  - docs/repos/casehub-openclaw.md
  - docs/new-repo-checklist.md
violation_hint: "A python/ directory appears in <module> list in pom.xml, or Python sources are placed inside a Java Maven module's src/ tree"
created: 2026-05-25
---

When an integration-tier repo needs a Python component (e.g. an OpenClaw plugin, a CLI wrapper, or an SDK), place it in a `python/` directory at the repo root with its own `pyproject.toml`. This directory is not declared as a Maven `<module>` — it has a completely independent build lifecycle (pip/poetry, published to PyPI independently). The Maven build produces Java artifacts; the Python build produces a separate Python package. Maven's `exec-maven-plugin` may invoke Python for integration tests but must not own the Python packaging. Alternatives considered and rejected: polyglot Maven pom.yaml (poor tooling support), Maven module containing Python sources (forces all consumers to configure Python toolchain), single packaging combining Java and Python (incompatible artifact models).
