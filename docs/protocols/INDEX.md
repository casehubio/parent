# Platform Protocols Index

Rules and conventions shared across casehubio repos. Each file is self-contained and retrievable independently.

## CaseHub-Specific Protocols

See [casehub/FOUNDATION-INDEX.md](casehub/FOUNDATION-INDEX.md) for the full table.

Quick reference:

| Protocol | One-liner |
|----------|-----------|
| [casehub/message-dispatch-builder-validation.md](casehub/message-dispatch-builder-validation.md) | Validate at build(), not downstream |
| [casehub/message-service-dispatch-enforcement-gate.md](casehub/message-service-dispatch-enforcement-gate.md) | dispatch() is the only write path |
| [casehub/ledger-algorithm-transparent-signing.md](casehub/ledger-algorithm-transparent-signing.md) | Derive algorithm from key, never hardcode |
| [casehub/cross-repo-optional-dep-table-registration.md](casehub/cross-repo-optional-dep-table-registration.md) | Register optional cross-repo deps in both places |
| [casehub/casehub-platform-dependency-scope.md](casehub/casehub-platform-dependency-scope.md) | test vs runtime scope for casehub-platform |
| [casehub/flyway-ledger-migration-locations.md](casehub/flyway-ledger-migration-locations.md) | Include db/ledger/migration in Flyway locations |
| [casehub/dual-trail-audit-pattern.md](casehub/dual-trail-audit-pattern.md) | Operational trail ≠ compliance ledger; CDI event required |
| [casehub/alternative-extension-patterns.md](casehub/alternative-extension-patterns.md) | @Alternative: ledger vs work extension patterns |
| [casehub/auth-retrofit-readiness.md](casehub/auth-retrofit-readiness.md) | Keep auth addable; gateway topology |

## Universal Protocols

See [universal/INDEX.md](universal/INDEX.md) for the full table.

| Protocol | One-liner |
|----------|-----------|
| [universal/no-jpa-entities-across-requires-new.md](universal/no-jpa-entities-across-requires-new.md) | Extract primitives before REQUIRES_NEW boundary |
| [universal/flyway-extension-migration-registration.md](universal/flyway-extension-migration-registration.md) | Repo-scoped migration paths + NativeImageResourcePatternsBuildItem; consumers configure quarkus.flyway.locations explicitly |
