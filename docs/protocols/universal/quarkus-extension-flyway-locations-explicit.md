---
id: PP-20260521-091cce
title: "Quarkus extensions must not ship quarkus.flyway.locations in runtime application.properties"
type: rule
scope: universal
applies_to: "Any Quarkus extension that ships Flyway migrations"
severity: important
refs:
  - casehub/flyway-version-range-allocation.md
violation_hint: "An extension that ships quarkus.flyway.locations in its runtime JAR replaces Quarkus's built-in default (db/migration), silently preventing consumers from running their own domain migrations if they have not also set the property."
garden_ref: "GE-20260521-977e3e"
created: 2026-05-21
---

When a Quarkus extension ships Flyway migrations at a dedicated path (e.g. `classpath:db/ledger/migration`), it must **not** configure `quarkus.flyway.locations` in a runtime `application.properties` bundled inside the extension JAR. Extension-provided config is the lowest-priority default: a consumer who has not set `quarkus.flyway.locations` inherits it, losing the Quarkus built-in default of `db/migration` and thus any domain migrations stored there. Instead, document the required path in the extension README or DESIGN.md, expose a build-time warning (see `@Produce(ArtifactResultBuildItem.class)`) if the consumer omits it, and let the consumer own the full `quarkus.flyway.locations` value for their datasource.
