# Universal Protocols

| File | Rule Summary | Applies To |
|------|-------------|------------|
| [no-jpa-entities-across-requires-new.md](no-jpa-entities-across-requires-new.md) | No JPA entities cross a REQUIRES_NEW boundary — extract primitives before the call | Any Quarkus service with REQUIRES_NEW + outer @Transactional |
| [vertical-slice-planning.md](vertical-slice-planning.md) | Identify vertical slices before implementing layers; order by sequential dependency then minimal delta; LAYER-LOG.md opens with a slice index | Any layered CaseHub application |
| [flyway-extension-migration-registration.md](flyway-extension-migration-registration.md) | Extensions use repo-scoped `db/<repo>/migration/` paths + `NativeImageResourcePatternsBuildItem`; Quarkus consumers must configure `quarkus.flyway.locations` explicitly — no runtime auto-registration exists | Any Quarkus extension shipping Flyway migrations |
