---
id: PP-20260521-88a52d
title: "casehub-work Hibernate scan requires both runtime.model and runtime.filter packages"
type: rule
scope: application
applies_to: "Any Quarkus app consuming casehub-work with explicit quarkus.hibernate-orm.packages"
severity: important
refs:
  - GE-20260513-74dc72
violation_hint: "FilterRule entity not found at startup. Symptom: label-based routing fails or Hibernate metadata error with no clear indication of the missing package."
created: 2026-05-21
---

When configuring explicit Hibernate ORM package scanning for an app that includes casehub-work, both packages are required:

```properties
quarkus.hibernate-orm.packages=io.casehub.work.runtime.model,io.casehub.work.runtime.filter,...
```

`io.casehub.work.runtime.filter` contains `FilterRule`, a JPA entity used by casehub-work's label-based routing feature. Omitting it causes a silent startup failure — the error message names `FilterRule` but does not identify the missing package.

The `runtime.model` package alone is insufficient even if the app does not use label-based routing directly — `FilterRule` is always scanned as part of the casehub-work entity set.
