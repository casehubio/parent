# Platform Protocols Index

Rules and conventions shared across casehubio repos. Each file is self-contained and retrievable independently.

## CaseHub-Specific Protocols

See [casehub/FOUNDATION-INDEX.md](casehub/FOUNDATION-INDEX.md) for the full table.

Quick reference:

| Protocol | One-liner |
|----------|-----------|
| [casehub/trust-maturity-model.md](casehub/trust-maturity-model.md) | Four-phase trust cold-start model; all dimensions higher = better; bootstrap > borderline |
| [casehub/external-api-surface-in-deep-dive.md](casehub/external-api-surface-in-deep-dive.md) | External API surface belongs in docs/repos/ deep-dive, not deferred to DESIGN.md |
| [casehub/protocol-refs-use-double-dotdot.md](casehub/protocol-refs-use-double-dotdot.md) | Protocol refs from docs/protocols/casehub/ use ../../ prefix |
| [casehub/consumer-spi-placement.md](casehub/consumer-spi-placement.md) | Consumer-facing SPIs in api/<domain>/, not runtime/ |
| [casehub/message-dispatch-builder-validation.md](casehub/message-dispatch-builder-validation.md) | Validate at build(), not downstream |
| [casehub/message-service-dispatch-enforcement-gate.md](casehub/message-service-dispatch-enforcement-gate.md) | dispatch() is the only write path |
| [casehub/ledger-algorithm-transparent-signing.md](casehub/ledger-algorithm-transparent-signing.md) | Derive algorithm from key, never hardcode |
| [casehub/cross-repo-optional-dep-table-registration.md](casehub/cross-repo-optional-dep-table-registration.md) | Register optional cross-repo deps in both places |
| [casehub/casehub-platform-dependency-scope.md](casehub/casehub-platform-dependency-scope.md) | test vs runtime scope for casehub-platform |
| [casehub/flyway-ledger-migration-locations.md](casehub/flyway-ledger-migration-locations.md) | Include db/ledger/migration in Flyway locations |
| [casehub/dual-trail-audit-pattern.md](casehub/dual-trail-audit-pattern.md) | Operational trail ≠ compliance ledger; CDI event required |
| [casehub/alternative-extension-patterns.md](casehub/alternative-extension-patterns.md) | @Alternative: ledger vs work extension patterns |
| [casehub/auth-retrofit-readiness.md](casehub/auth-retrofit-readiness.md) | Keep auth addable; gateway topology |
| [casehub/ledger-hash-chain-disabled-in-h2-tests.md](casehub/ledger-hash-chain-disabled-in-h2-tests.md) | Disable Merkle hash chain in H2 @QuarkusTest — concurrent Quartz races on frontier |
| [casehub/engine-investigation-test-drain.md](casehub/engine-investigation-test-drain.md) | Drain every investigation test to 'completed' before returning |
| [casehub/memory-storeall-transactional-contract.md](casehub/memory-storeall-transactional-contract.md) | storeAll() overrides: single @Transactional, per-item assertTenant, no partial writes |
| [casehub/workitem-template-constraints-snapshot-at-instantiation.md](casehub/workitem-template-constraints-snapshot-at-instantiation.md) | Snapshot template constraints (outcomes, schemas) onto WorkItem at instantiation; never re-read at completion |

## Universal Protocols

See [universal/INDEX.md](universal/INDEX.md) for the full table.

| Protocol | One-liner |
|----------|-----------|
| [universal/no-jpa-entities-across-requires-new.md](universal/no-jpa-entities-across-requires-new.md) | Extract primitives before REQUIRES_NEW boundary |
| [universal/flyway-extension-migration-registration.md](universal/flyway-extension-migration-registration.md) | Repo-scoped migration paths + NativeImageResourcePatternsBuildItem; consumers configure quarkus.flyway.locations explicitly |
