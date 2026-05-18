# CaseHub Foundation Protocols

For LLMs building the CaseHub platform itself — foundation modules, SPIs, and extensions
(casehub-engine, casehub-ledger, casehub-work, casehub-qhorus, casehub-connectors, parent).

**Building an app on CaseHub?** Read [HARNESS-INDEX.md](HARNESS-INDEX.md) instead.

Reconstitute this index: `grep -rl "^scope: platform\|^scope: repo" docs/protocols/*.md`

---

## Protocols

| File | Rule | Applies to |
|------|------|------------|
| [auth-retrofit-readiness.md](casehub/auth-retrofit-readiness.md) | No auth in domain/service; thin REST resources; injectable query filters; auth-free SPI signatures | All casehubio repos |
| [subcase-coordination-strategy.md](casehub/subcase-coordination-strategy.md) | Native M-of-N counting for simple thresholds; quarkus-flow for conditional/sequential orchestration; always behind SPI | casehub-engine blackboard |
| [flyway-migration-rules.md](universal/flyway-migration-rules.md) | Flyway namespace ranges, H2 mode, PostgreSQL testing | All modules with Flyway |
| [flyway-version-range-allocation.md](casehub/flyway-version-range-allocation.md) | Each module owns an exclusive Flyway thousand-block version range | All casehub modules using Flyway |
| [optional-module-pattern.md](universal/optional-module-pattern.md) | Optional Jandex library module pattern | All optional feature modules |
| [quarkus-test-database.md](universal/quarkus-test-database.md) | Database configuration for @QuarkusTest suites | All modules with @QuarkusTest |
| [maven-module-scoping.md](universal/maven-module-scoping.md) | Always specify `-pl <module>` when running Maven commands | All multi-module casehub modules |
| [maven-submodule-folder-naming.md](universal/maven-submodule-folder-naming.md) | Submodule folder names are short — no repo prefix; `api`, `runtime`, `deployment` etc. | All multi-module casehub repos |
| [module-tier-structure.md](universal/module-tier-structure.md) | Three-tier module structure — pure-Java SPI / core library (no JPA) / full extension; no SDK types in SPI signatures | All casehubio multi-module repos |
| [quartz-ram-store-configuration.md](universal/quartz-ram-store-configuration.md) | Use Quartz RAM store — no JDBC store, no Quartz tables | All casehub modules using Quartz |
| [ledger-spi-propagation.md](casehub/ledger-spi-propagation.md) | When a LedgerEntryRepository SPI method is added, update all downstream implementations | casehub-work, casehub-qhorus, casehub-engine |
| [ledger-sync-async-parity.md](casehub/ledger-sync-async-parity.md) | New ledger service methods must ship both blocking and reactive variants | LedgerVerificationService, LedgerEntryRepository, KeyRotationService, any future ledger service SPI |
| [ledger-subclass-extension.md](casehub/ledger-subclass-extension.md) | Ledger subclass rules — JOINED inheritance, V1004+ consumer migrations, domain-agnostic leaf hash | Any repo adding a LedgerEntry JPA subclass |
| [spi-default-method-contract-test.md](universal/spi-default-method-contract-test.md) | Verify SPI default method contracts with an anonymous implementation test — compiler error is the RED state | All SPI interfaces using default methods |
| [qhorus-event-content-null.md](casehub/qhorus-event-content-null.md) | EVENT message `content` is always null — render telemetry fields instead | All projects reading Qhorus ledger entries |
| [qhorus-human-governance-channel-types.md](casehub/qhorus-human-governance-channel-types.md) | Oversight channel must have `allowedTypes=QUERY,COMMAND`; human actors never post EVENT | All projects using Qhorus NormativeChannelLayout |
| [qhorus-actor-type-mapping.md](casehub/qhorus-actor-type-mapping.md) | All ActorType values must map to the canonical casehub ledger vocabulary | All casehubio projects assigning ActorType |
| [gateway-backend-registration-ordering.md](casehub/gateway-backend-registration-ordering.md) | Call open() before registerBackend() when registering a ChannelBackend | casehub-qhorus: any code calling ChannelGateway.registerBackend() |
| [maven-coordinate-standard.md](universal/maven-coordinate-standard.md) | Maven coordinate standard for all casehubio repos | All casehubio Maven repos |
| [artifact-rename-propagation.md](universal/artifact-rename-propagation.md) | Artifact rename propagation — update all cross-repo consumers before shipping | Any casehubio repo renaming a published artifactId |
| [java-optional-usage.md](universal/java-optional-usage.md) | Use Optional only when absence is the method's primary return contract | All Java code across casehub |
| [quarkus-test-security-http-only.md](universal/quarkus-test-security-http-only.md) | Only add @TestSecurity to @QuarkusTest classes that exercise HTTP endpoints | All modules with @QuarkusTest classes |
| [quarkus-optional-extension-dep.md](universal/quarkus-optional-extension-dep.md) | Gate optional Quarkus extension deps via @IfBuildProperty on natural datasource property, not ExcludedTypeBuildItem | Quarkus extension runtime and deployment modules |
| [engine-spi-noops-defaultbean.md](casehub/engine-spi-noops-defaultbean.md) | Engine SPI no-op defaults must use @DefaultBean — bare @ApplicationScoped collides with consumer implementations | casehub-engine runtime no-op SPI beans |
| [case-definition-layers.md](casehub/case-definition-layers.md) | Three-layer case definition architecture (YAML → schema model → canonical API model + fluent DSL) — inherited from Serverless Workflow 1.0; do not collapse layers or bypass CaseDefinitionYamlMapper | casehub-engine; all CaseHub agentic harnesses |
| [typed-preference-keys.md](casehub/typed-preference-keys.md) | Use typed PreferenceKey<T> for SPI configuration — never stringly-typed get(String, Class<?>) | All casehubio SPI configuration and preference resolution |
| [platform-spi-contract.md](casehub/platform-spi-contract.md) | Platform SPI implementation contract — @DefaultBean mock scope, @RequestScoped real impl scope, Preference DEFAULT constant pattern | All repos implementing casehub-platform-api SPIs |
| [work-adapter-test-subcase-group-repository.md](casehub/work-adapter-test-subcase-group-repository.md) | work-adapter @QuarkusTest requires MemorySubCaseGroupRepository in selected-alternatives | casehub-engine-work-adapter test module |
| [work-adapter-plan-item-running-ordering.md](casehub/work-adapter-plan-item-running-ordering.md) | PlanItem must not be marked RUNNING until all resolution and validation steps succeed | casehub-engine-work-adapter outbound handlers |
| [work-adapter-inputmapping-payload-contract.md](casehub/work-adapter-inputmapping-payload-contract.md) | Engine adapters must propagate HumanTaskTarget inputMapping output to WorkItem payload | casehub-engine-work-adapter outbound handlers |

---

## Garden References

Generic Quarkus/Java knowledge not specific to CaseHub. These apply to harness builders too —
referenced here; [HARNESS-INDEX.md](HARNESS-INDEX.md) points back to this section.

### CDI / Transactions

| GE-ID | Title |
|---|---|
| GE-20260512-66d997 | Panache static methods bypass CDI @Alternative stores — returns empty results silently |
| GE-20260512-0fe012 | CDI fireAsync() inside @Transactional dispatches immediately — observer can run before commit |
| GE-20260512-6887c9 | @ObservesAsync + @Transactional on same method is unreliable — delegate to separate bean |
| GE-20260512-a9ad9f | Raw ExecutorService drops CDI context — @Transactional silently broken on background threads |
| GE-20260512-6d0c2b | BroadcastProcessor.onNext() throws BackPressureFailure when no subscribers are registered |

### Quarkus Testing

| GE-ID | Title |
|---|---|
| GE-20260512-47f92e | quarkus-junit5 is a relocation stub since Quarkus 3.31 — use quarkus-junit |
| GE-20260512-b3f32a | @IfBuildProperty/@UnlessBuildProperty evaluated at augmentation only — QuarkusTestProfile has no effect |
| GE-20260512-e552f7 | @ApplicationScoped bean state persists across @QuarkusTest classes — tests pass in isolation, fail in suite |
| GE-20260512-50b394 | Use @TestTransaction + unique identifiers to prevent @Scheduled interference in tests |
| GE-20260512-c246b0 | Test CDI SPI with @Alternative static inner classes — Mockito cannot be injected as CDI beans |
| GE-20260512-493c90 | @QuarkusTest classes named *IT.java silently report 0 tests — failsafe collects them, not surefire |
| GE-20260512-c30f52 | @QuarkusIntegrationTest in runtime module causes class loading failures — separate module required |
| GE-20260513-3c1a03 | @TestSecurity silently ignored on @QuarkusTest classes that never touch HTTP |
| GE-20260513-4c4205 | Use AtomicInteger call counter in Supplier<String> to distinguish SSE events by content in tests |

### Database / Schema / Migrations

| GE-ID | Title |
|---|---|
| GE-20260512-ea776c | Quarkus named persistence units silently skip schema generation — explicit config per named PU |
| GE-20260512-a3838e | Transitive hibernate-reactive-panache causes H2 test startup failure — disable reactive datasource |
| GE-20260512-7720ab | H2-reserved words as column names pass PostgreSQL but fail in H2 test mode |
| GE-20260512-2c2eff | Non-ANSI SQL types in Flyway migrations pass H2 silently but fail on PostgreSQL at deployment |
| GE-20260512-67b3b5 | Panache find() alias-prefixed field names return empty results silently — bare field names required |

### Scheduler / Config

| GE-ID | Title |
|---|---|
| GE-20260512-1fa51e | @Scheduled interval without $ prefix silently fires at wrong frequency |
| GE-20260512-552405 | @ConfigMapping methods without Javadoc cause a compile error — not a runtime warning |
| GE-20260512-523f68 | Quarkus dev mode hot-reload silently breaks WebSocket endpoint registration |

### Architecture / Design Techniques

| GE-ID | Title |
|---|---|
| GE-20260512-e3e525 | OCC + policyTriggered flag for M-of-N threshold completion — prevents duplicate trigger under READ COMMITTED |
| GE-20260512-a09bd3 | Enforce blocking/reactive SPI method parity with a reflection test |

### Tooling

| GE-ID | Title |
|---|---|
| GE-20260512-a28ecc | Maven relative paths resolve to wrong worktree when shell cwd changes — use absolute paths |
