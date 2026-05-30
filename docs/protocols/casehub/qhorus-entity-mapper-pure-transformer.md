---
id: PP-20260530-0c33a2
title: "QhorusEntityMapper methods must not inject stores or issue queries — all data arrives as parameters"
type: rule
scope: repo
applies_to: "casehub-qhorus — QhorusEntityMapper and any future mapper class in io.casehub.qhorus.runtime"
severity: important
refs:
  - casehub/qhorus-service-store-seam.md
violation_hint: "QhorusEntityMapper injects a *Store interface, or a toChannelDetail() / toTimelineEntry() method calls findX() on any store. A 2-arg toChannelDetail(Channel, long) that internally queries ChannelBindingStore is the canonical violation."
created: 2026-05-30
---

`QhorusEntityMapper` is a pure transformer: it receives entity data and supplementary domain objects as method parameters and maps them to API DTOs — no CDI store injections, no database queries, no side effects. The Option B pattern (caller supplies `Optional<ChannelConnectorBinding>` alongside the `Channel`) is correct; the Option A pattern (mapper injects `ChannelBindingStore` and queries per-entity) is the violation. Option A hides N+1 query chains inside mapping code, makes the mapper untestable without a live datasource, and prevents callers from pre-loading data in batch. When supplementary data is needed, the caller loads it (individually or in bulk via `findAll()`) and passes it to the mapper — the mapper never decides when or how to fetch. See `qhorus-service-store-seam.md` for the complementary rule governing services.
