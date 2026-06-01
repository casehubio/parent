---
id: PP-20260601-aec35f
title: "Use @InjectMock for SPI override tests — not @TestProfile + @Alternative"
type: rule
scope: application
applies_to: "Any @QuarkusTest that needs to override a CasHub SPI or @DefaultBean implementation"
severity: important
refs:
  - docs/protocols/casehub/alternative-extension-patterns.md
violation_hint: "@TestProfile with getEnabledAlternatives() returning only the test bean; @Alternative inner class inside a @TestProfile class"
created: 2026-06-01
---

When a `@QuarkusTest` needs to inject a custom SPI implementation (e.g. a policy bean for an isolated test), use `@InjectMock` on the SPI field rather than `@TestProfile` with `getEnabledAlternatives()`. The `getEnabledAlternatives()` mechanism **replaces** the `quarkus.arc.selected-alternatives` property rather than merging with it — omitting any `@Alternative` from the set (e.g. `MemoryPlanItemStore`, `MemorySubCaseGroupRepository`, `JpaLedgerEntryRepository`) silently deactivates those beans for the profile, causing startup failures. `@InjectMock` creates a Mockito mock that replaces the CDI bean for the duration of the test class without touching `selected-alternatives`, leaving standard test configuration intact.
