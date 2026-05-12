---
id: PP-20260513-7c227e
title: "Only add @TestSecurity to @QuarkusTest classes that exercise HTTP endpoints"
type: rule
scope: platform
applies_to: "All modules with @QuarkusTest classes"
severity: guidance
refs: []
violation_hint: "@TestSecurity present on a test class that never calls RestAssured, @TestHTTPEndpoint, or any HTTP client"
created: 2026-05-13
---

`@TestSecurity` works by registering a Quarkus security identity for the active HTTP request context. When a `@QuarkusTest` class injects CDI beans and calls their methods directly — without any RestAssured call or HTTP client — there is no request context and the annotation has no effect. Quarkus emits no warning; the test passes and the annotation silently misleads readers. Only add `@TestSecurity` to classes that exercise HTTP endpoints. CDI-only tests need no security identity and should omit it.
