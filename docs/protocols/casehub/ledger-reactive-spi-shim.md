---
id: PP-20260519-3f2ea2
title: "Reactive repository SPIs in casehub-ledger ship no bundled JPA impl and provide a @DefaultBean blocking test shim"
type: rule
scope: repo
applies_to: "Any new reactive repository SPI added to casehub-ledger (e.g. ReactiveKeyRotationRepository)"
severity: important
refs:
  - docs/specs/2026-05-19-reactive-key-rotation-design.md
violation_hint: "A reactive SPI with a bundled JpaReactiveXxx implementation, or a @QuarkusTest suite that fails CDI startup because no @DefaultBean satisfies the reactive injection point"
created: 2026-05-19
---

casehub-ledger provides SPI contracts for reactive repository access but bundles no
production JPA implementation — consumers supply their own (Hibernate Reactive, reactive
MongoDB, etc.). Alongside the SPI interface, a @DefaultBean @ApplicationScoped blocking
shim must be placed in test/java, wrapping the blocking JPA implementation with
Uni.createFrom().item(). This allows the H2/JDBC @QuarkusTest suite to resolve reactive
injections without a Vert.x datasource. The shim stays in test sources and never ships.
