---
id: PP-20260521-1f24aa
title: "Choose reactive vs blocking based on I/O profile and concurrency model — never mix within a request path"
type: principle
scope: universal
applies_to: "Any Quarkus/Vert.x-based module making an architectural choice between reactive and blocking execution"
severity: important
refs:
  - docs/protocols/universal/reactive-blocking-tier-separation.md
  - docs/protocols/casehub/reactive-service-build-gating.md
violation_hint: "Module chosen blocking due to build constraints (e.g. reactive injection failure), not architectural reasoning. Or: reactive and blocking code mixed in the same request path without an explicit handoff."
created: 2026-05-21
---

## Selection principle

Choose **reactive** when the module is:
- I/O-bound with many concurrent requests — event loop threads handle more load than a blocking thread pool
- Event-driven — input arrives as messages, CDI events, or Vert.x bus deliveries
- Streaming — responses are assembled incrementally
- Latency-sensitive with high concurrency — park the event loop thread on I/O causes head-of-line blocking

Choose **blocking** when the module is:
- Naturally transactional — a unit of work either commits or rolls back as a whole
- Rules-heavy or computationally intensive — CPU-bound work belongs on worker threads
- Sequential per entity — each request processes one entity fully before the next
- Batch — scheduled jobs, migration runners, report generation

The persistence model must follow the execution model: reactive execution → reactive datasource (Hibernate Reactive, Mutiny); blocking → standard JPA/JDBC. Mismatching them (reactive execution + JDBC) causes Vert.x IO thread blocking errors.

## Never mix within a request path

A request that starts reactive must stay reactive. A request that starts blocking must stay blocking. Switching execution contexts within a single request path requires an explicit handoff (`@Blocking` annotation, `executeBlocking()`, or an async boundary) and must be a deliberate architectural decision — not an accident of injection.

## Quarkus-specific mechanism

| Model | Configuration |
|-------|--------------|
| Blocking | `@Blocking` on REST methods, `@Transactional`, standard JPA, RESTEasy Classic |
| Reactive | Reactive Routes or RESTEasy Reactive, `quarkus.datasource.reactive=true`, Hibernate Reactive, Mutiny `Uni<T>` / `Multi<T>` |

When a module must serve both blocking and reactive consumers, see PP-20260519-f2e160 (reactive-blocking-tier-separation) for the structural split, and PP-20260519-39a9a5 (reactive-service-build-gating) for the Quarkus build-time gating mechanism.

## Module evaluation (casehub)

| Module | Model | Reasoning |
|--------|-------|-----------|
| casehub-aml | Blocking | Rules-heavy, transactional AML records, batch risk scoring |
| casehub-clinical | Blocking | Transactional clinical records, FDA audit chain |
| casehub-qhorus | Reactive | Event-driven messaging, high concurrency channel delivery |
| casehub-work | Blocking (core) | Transactional work-item lifecycle; queue/flow processing may warrant reactive subset |
| casehub-devtown | TBD | Has async queues and GitHub integration — evaluate when implementing |
