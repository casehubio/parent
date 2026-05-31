# Universal Protocols

| File | Rule Summary | Applies To |
|------|-------------|------------|
| [no-jpa-entities-across-requires-new.md](no-jpa-entities-across-requires-new.md) | No JPA entities cross a REQUIRES_NEW boundary — extract primitives before the call | Any Quarkus service with REQUIRES_NEW + outer @Transactional |
| [vertical-slice-planning.md](vertical-slice-planning.md) | Identify vertical slices before implementing layers; order by sequential dependency then minimal delta; LAYER-LOG.md opens with a slice index | Any layered CaseHub application |
| [flyway-extension-migration-registration.md](flyway-extension-migration-registration.md) | Extensions use repo-scoped `db/<repo>/migration/` paths + `NativeImageResourcePatternsBuildItem`; Quarkus consumers must configure `quarkus.flyway.locations` explicitly — no runtime auto-registration exists | Any Quarkus extension shipping Flyway migrations |
| [sanitize-caller-controlled-headers-before-logging.md](sanitize-caller-controlled-headers-before-logging.md) | Validate caller-controlled headers (X-Forwarded-For etc.) against a strict allowlist before including in logs — especially SECURITY: log lines | Any Quarkus service logging HTTP request context |
| [persistence-backend-cdi-priority.md](persistence-backend-cdi-priority.md) | `@DefaultBean` → `@ApplicationScoped` → `@Alternative @Priority(1)` — persistence backends activate by classpath presence alone; includes reactive bridge variant and Maven scope rules | Any module shipping a persistence SPI with optional backend implementations |
| [quarkus-extension-unremovable-consumer-beans.md](quarkus-extension-unremovable-consumer-beans.md) | Extension CDI beans with no internal injection point must be `@Unremovable` — ARC silently removes them otherwise, causing UnsatisfiedResolutionException in consumers | Any Quarkus extension publishing beans intended for consumer injection with no self-use |
