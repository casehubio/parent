---
id: PP-20260602-fb90a6
title: "SPIs with only test-scoped implementations need a @DefaultBean no-op in the runtime module"
type: rule
scope: platform
applies_to: "Any casehub-work runtime module that injects a platform SPI whose only concrete implementation is in a test-scoped dependency"
severity: important
refs:
  - ../../repos/casehub-work.md
violation_hint: "UnsatisfiedResolutionException at startup — CDI cannot satisfy the SPI injection point because the Mock* implementation is test-scope only and not on the production classpath."
created: 2026-06-02
---

When a platform SPI (e.g. `GroupMembershipProvider`, `ExclusionPolicy`) has no production implementation on the runtime classpath — because its only concrete impl (`Mock*`) lives in a test-scoped dependency — add a no-op `@DefaultBean @ApplicationScoped` to the runtime module. The no-op returns a safe empty/pass-through result and satisfies CDI at startup. Production deployments override it with `@Alternative @Priority(1)`. Without this, startup fails with `UnsatisfiedResolutionException` in any deployment that does not supply its own implementation.
