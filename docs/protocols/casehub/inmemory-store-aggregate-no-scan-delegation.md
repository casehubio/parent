---
id: PP-20260529-19711d
title: "InMemoryStore aggregate methods must not delegate to scan() — stream the backing collection directly"
type: rule
scope: repo
applies_to: "casehub-qhorus-testing — InMemory*Store implementations of count(), sum(), or any aggregate method"
severity: important
refs:
  - docs/specs/2026-05-28-watchdog-store-seam-design.md
violation_hint: "An InMemoryStore.count(query) method calls scan(query).size() or scan(query).stream().count() — scan() applies limit, so results are silently truncated."
created: 2026-05-29
---

`InMemory*Store` methods that compute aggregates (count, sum, distinct) must stream the backing collection directly — never delegate to `scan()`. Panache `scan()` / `find()` methods apply pagination fields (`limit`, `afterId`) that are semantically correct for list queries but wrong for aggregates. `scan(q).size()` returns at most `q.limit()` items, silently giving wrong counts for queries that carry a limit. The correct pattern: `store.values().stream().filter(q::matches).count()`. The `matches(entity)` predicate on the query object does not apply `limit` — it is a per-entity filter only.
