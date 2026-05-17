---
id: PP-20260517-4b61ae
title: "Do not throw IllegalStateException in REST-reachable code in casehub-work consumers"
type: rule
scope: application
applies_to: All CaseHub agentic harnesses that depend on casehub-work
severity: important
refs:
  - docs/protocols/casehub/HARNESS-INDEX.md
violation_hint: "REST endpoint returns HTTP 409 Conflict unexpectedly — caused by casehub-work's IllegalStateExceptionMapper mapping IllegalStateException to 409"
created: 2026-05-17
---

`casehub-work` ships `IllegalStateExceptionMapper`, a JAX-RS `ExceptionMapper<IllegalStateException>` that maps every `IllegalStateException` to HTTP 409 Conflict. This applies globally to any REST request in the application — not just code within casehub-work. Throw `RuntimeException` or a custom unchecked exception subclass for infrastructure failures (timeouts, missing CDI beans, poll failures) that should produce HTTP 500. Reserve `IllegalStateException` only for genuine domain state violations where 409 is the intended response.
