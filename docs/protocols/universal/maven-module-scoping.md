---
id: PP-20260508-4bfd3a
title: "Always scope Maven commands to a specific module with -pl"
type: rule
scope: universal
applies_to: "All multi-module casehub modules"
severity: important
refs: []
violation_hint: "Running without -pl times out or rebuilds unintended modules, hiding the real build result"
created: 2026-05-08
---

# Convention: Always Scope Maven Commands to a Specific Module

**Applies to:** All multi-module casehub modules  
**Severity:** Important — running without -pl times out or rebuilds unintended modules

## Problem

`mvn test` or `mvn install` at the reactor root rebuilds all submodules, taking far too long and masking which module actually failed.

## Rule

Always specify `-pl <module>` when running Maven commands. Use the helper scripts in `scripts/` which enforce hard timeouts: `scripts/mvn-test` (90s), `scripts/mvn-install` (60s), `scripts/mvn-compile` (45s), `scripts/check-build`.

## Example

```bash
# Wrong — rebuilds all modules
mvn test

# Right
scripts/mvn-test quarkus-work-ledger
# or
mvn test -pl quarkus-work-ledger --batch-mode
```
