---
id: PP-20260521-78674a
title: "Use quarkus-junit not quarkus-junit5 in all new Quarkus modules"
type: rule
scope: universal
applies_to: "All Maven modules that declare quarkus-junit5 as a test dependency"
severity: guidance
refs: []
violation_hint: "<artifactId>quarkus-junit5</artifactId> in any pom.xml test dependency block"
created: 2026-05-21
---

Quarkus 3.31 relocated `quarkus-junit5` to `quarkus-junit`. Both artifact IDs resolve via Maven relocation, but `quarkus-junit5` emits a deprecation warning on every build. New modules must declare `quarkus-junit` as the test dependency. Existing modules that still use `quarkus-junit5` should be migrated — tracked in casehubio/platform#19 as the canonical migration issue. The two artifact IDs are functionally identical; the change is purely the `<artifactId>` in `pom.xml`.
