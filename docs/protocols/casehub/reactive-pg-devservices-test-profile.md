---
id: PP-20260528-ac6d93
title: "Use Quarkus Dev Services named-datasource profile for reactive PostgreSQL integration tests"
type: rule
scope: platform
applies_to: "Any casehubio module with a named datasource that adds reactive PostgreSQL integration tests"
severity: guidance
refs:
  - ../../PLATFORM.md
violation_hint: "Using Testcontainers directly, hardcoding a PostgreSQL JDBC URL, or putting reactive-pg config in the default %test profile (which breaks H2-only builds)"
created: 2026-05-28
---

Modules that need reactive PostgreSQL integration tests use a named Quarkus config profile (e.g. `%reactive-pg`) in `src/test/resources/application.properties`, scoped to the named datasource: `db-kind=postgresql`, `devservices.enabled=true`, `devservices.image-name=postgres:17-alpine`, `reactive=true`, `jdbc=true`, `flyway.migrate-at-start=true`, `hibernate-orm.database.generation=none`. The default `%test` profile stays H2 in-memory with `devservices.enabled=false`. The reactive profile is activated by a `QuarkusTestProfile` subclass returning the profile name via `getConfigProfile()`. Tests using it are annotated `@TestProfile(ReactiveXxxTestProfile.class)` and are not run in the default `mvn test`. Established in casehub-eidos and casehub-qhorus; applied to claudony's named `qhorus` datasource in claudony#116.
