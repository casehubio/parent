---
id: PP-20260529-6047d2
title: "QuarkusTestProfile restart requires casehub.ledger.datasource in getConfigOverrides() when ledger JPA is used"
type: rule
scope: repo
applies_to: "Any @QuarkusTest class whose @TestProfile causes a Quarkus context restart AND uses casehub-ledger JPA beans (JpaActorTrustScoreRepository, LedgerWriteService, TrustGateService, etc.)"
severity: important
refs:
  - docs/protocols/casehub/flyway-ledger-migration-locations.md
violation_hint: "Test fails with UnknownNamedQueryException on ActorTrustScore or ledger entity named queries after a profile restart — @LedgerPersistenceUnit routes to the default PU where ledger named queries are not registered."
created: 2026-05-29
---

When a `QuarkusTestProfile` causes a Quarkus context restart (triggered by using a different profile class than the previous test class), `application.properties` is not re-read for the new context — only `getConfigOverrides()` is applied. The `casehub.ledger.datasource=<name>` property routes `@LedgerPersistenceUnit` EntityManager to a named persistence unit; omitting it from `getConfigOverrides()` routes the ledger to the default PU, where ledger named queries (`ActorTrustScore`, `LedgerEntry`, etc.) are not registered. Any `QuarkusTestProfile` that (a) causes a context restart and (b) exercises ledger JPA beans must include `config.put("casehub.ledger.datasource", "<named-pu>")` in `getConfigOverrides()`, alongside the standard datasource block for the named PU.
