---
id: PP-20260508-7e206d
title: "Panache find() WHERE clauses use bare field names, not aliases"
type: rule
scope: platform
applies_to: "All modules using Panache for JPA queries"
severity: important
refs: []
violation_hint: "Alias-prefixed field names cause silent empty results, not an exception"
created: 2026-05-08
---

# Convention: Panache find() WHERE Clauses Use Bare Field Names, Not Aliases

**Applies to:** All modules using Panache for JPA queries  
**Severity:** Important — alias-prefixed field names cause silent empty results, not an exception

## Problem

Panache's `find()` and `list()` methods use a simplified HQL dialect. Writing `wi.assigneeId = :x` (alias-prefixed) silently produces zero results instead of throwing a query parse error.

## Rule

Use bare entity field names in Panache queries: `assigneeId = :x`, not `wi.assigneeId = :x` or `WorkItem.assigneeId = :x`.

## Example

```java
// Wrong — returns empty list silently
WorkItem.find("wi.assigneeId = :id", Map.of("id", userId));

// Right
WorkItem.find("assigneeId = :id", Map.of("id", userId));
```
