---
id: PP-20260529-10866a
title: "Tutorial harness layers use @DefaultBean (Layer 1) + @Alternative @Priority(N) (Layer N>1) for CDI displacement"
type: rule
scope: application
applies_to: "devtown, aml, clinical — any CaseHub tutorial harness implementing a layered learning progression"
severity: important
refs:
  - repos/casehub-devtown.md
violation_hint: "Two @ApplicationScoped beans implementing the same port interface without @DefaultBean or @Alternative → AmbiguousResolutionException at startup. OR: @Alternative @Priority ordering inverted (higher tutorial layer number has lower CDI priority) → wrong layer active in the full production build."
created: 2026-05-29
---

In a CaseHub tutorial harness, each implementation of a port interface follows a fixed CDI displacement ordering: Layer 1 (naive baseline) is `@ApplicationScoped @DefaultBean` and is never deleted; each subsequent Layer N (N > 1) is `@ApplicationScoped @Alternative @Priority(N)`, where the layer number IS the CDI priority. The highest-priority alternative wins in the full production build — lower-priority implementations exist on the classpath for tutorial reading but are CDI-inactive. To test a specific layer without a test profile, inject the concrete type directly (`@Inject QhorusPrReviewService`) — CDI always resolves concrete-type injection to exactly that bean regardless of priority ordering.
