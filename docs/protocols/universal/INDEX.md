# Universal Protocols

Reusable conventions for any Java/Quarkus project — not specific to CaseHub.
Staging area for eventual contribution to a shared Hortora protocols repository.

Any project using Hortora can adopt these. When a Hortora protocols home exists,
these files will be moved there and replaced with references.

Reconstitute: `grep -rl "^scope: universal" docs/protocols/universal/*.md`

---

## Maven / Build

| File | Rule | Applies to |
|------|------|------------|
| [maven-coordinate-standard.md](maven-coordinate-standard.md) | Maven coordinate standard — groupId, artifactId, version conventions | Any Maven project |
| [maven-module-scoping.md](maven-module-scoping.md) | Always specify `-pl <module>` when running Maven commands | Any multi-module Maven project |
| [maven-submodule-folder-naming.md](maven-submodule-folder-naming.md) | Submodule folder names are short — no parent prefix; `api`, `runtime`, `deployment` | Any multi-module Maven project |
| [artifact-rename-propagation.md](artifact-rename-propagation.md) | Artifact rename propagation — update all consumers before shipping | Any multi-repo Maven project |

## Java / Architecture

| File | Rule | Applies to |
|------|------|------------|
| [java-optional-usage.md](java-optional-usage.md) | Use Optional only when absence is the method's primary return contract | Any Java project |
| [module-tier-structure.md](module-tier-structure.md) | Three-tier module structure — pure-Java SPI / core library (no JPA) / full extension | Any library or framework |
| [optional-module-pattern.md](optional-module-pattern.md) | Optional Jandex library module pattern | Any library with optional features |
| [spi-default-method-contract-test.md](spi-default-method-contract-test.md) | Verify SPI default method contracts with an anonymous implementation test | Any library with SPIs and default methods |

## Quarkus

| File | Rule | Applies to |
|------|------|------------|
| [quarkus-test-database.md](quarkus-test-database.md) | Database configuration for @QuarkusTest suites | Any Quarkus app with @QuarkusTest |
| [quarkus-test-security-http-only.md](quarkus-test-security-http-only.md) | Only add @TestSecurity to @QuarkusTest classes that exercise HTTP endpoints | Any Quarkus app with @TestSecurity |
| [quartz-ram-store-configuration.md](quartz-ram-store-configuration.md) | Use Quartz RAM store — no JDBC store, no Quartz tables | Any Quarkus app using Quartz |
| [quarkus-optional-extension-dep.md](quarkus-optional-extension-dep.md) | Gate optional Quarkus extension deps via Capabilities + ExcludedTypeBuildItem | Any Quarkus extension |
| [flyway-migration-rules.md](flyway-migration-rules.md) | Flyway migration conventions — naming, H2 compatibility, PostgreSQL testing | Any project using Flyway |

## Application Design

| File | Rule | Applies to |
|------|------|------------|
| [layer-log.md](layer-log.md) | Maintain LAYER-LOG.md as definition of done per adoption layer | Any layered application built on a platform |
| [reactive-blocking-tier-separation.md](reactive-blocking-tier-separation.md) | Service beans must not carry dependencies on capabilities optional in consuming deployments — blocking and reactive tiers are separate beans | Any extension library with heterogeneous deployment contexts |
| [reactive-vs-blocking-selection.md](reactive-vs-blocking-selection.md) | Choose reactive vs blocking based on I/O profile and concurrency model — never mix within a request path; persistence model must follow execution model | Any Quarkus/Vert.x-based module choosing an execution model |
