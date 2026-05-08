---
id: PP-20260508-e597d4
title: "@QuarkusIntegrationTest must live in a separate Maven module from the runtime"
type: rule
scope: platform
applies_to: "All Quarkus extensions with integration tests"
severity: critical
refs: []
violation_hint: "Placing @QuarkusIntegrationTest in the runtime module causes class loading failures with no clear error"
created: 2026-05-08
---

# Convention: @QuarkusIntegrationTest Must Live in a Separate Maven Module

**Applies to:** All Quarkus extensions with integration tests  
**Severity:** Critical — placing @QuarkusIntegrationTest in the runtime module causes class loading failures

## Problem

`@QuarkusIntegrationTest` tests the packaged application, not the running CDI container. Placing them alongside `@QuarkusTest` classes in the runtime module causes the augmented artifact to be loaded twice, producing obscure `ClassCastException` or `CDIException`.

## Rule

All `@QuarkusIntegrationTest` classes must live in a dedicated `integration-tests/` submodule, separate from the extension runtime module.

## Example

```
casehub-work/
├── runtime/          ← @QuarkusTest classes here
├── deployment/
└── integration-tests/ ← @QuarkusIntegrationTest classes here
```
