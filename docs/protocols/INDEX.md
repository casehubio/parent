# Cross-Module Protocols

One file per rule. Each file is self-contained and retrievable independently. All files use YAML frontmatter with id, title, type, scope, applies_to, severity, refs, violation_hint, and created fields.

## Casehub-Specific Protocols

| File | Rule | Applies to |
|---|---|---|
| [auth-retrofit-readiness.md](auth-retrofit-readiness.md) | No auth in domain/service; thin REST resources; injectable query filters; auth-free SPI signatures | All casehubio repos |
| [flyway-migration-rules.md](flyway-migration-rules.md) | Flyway namespace ranges, H2 mode, PostgreSQL testing | All modules with Flyway |
| [flyway-version-range-allocation.md](flyway-version-range-allocation.md) | Each module owns an exclusive Flyway thousand-block version range | All casehub modules using Flyway |
| [optional-module-pattern.md](optional-module-pattern.md) | Optional Jandex library module pattern | All optional feature modules |
| [quarkus-test-database.md](quarkus-test-database.md) | Database configuration for @QuarkusTest suites | All modules with @QuarkusTest |
| [maven-module-scoping.md](maven-module-scoping.md) | Always specify `-pl <module>` when running Maven commands | All multi-module casehub modules |
| [maven-submodule-folder-naming.md](maven-submodule-folder-naming.md) | Submodule folder names are short — no repo prefix; `api`, `runtime`, `deployment` etc. | All multi-module casehub repos |
| [module-tier-structure.md](module-tier-structure.md) | Three-tier module structure — pure-Java SPI / core library (no JPA) / full extension; no SDK types in SPI signatures | All casehubio multi-module repos |
| [quartz-ram-store-configuration.md](quartz-ram-store-configuration.md) | Use Quartz RAM store — no JDBC store, no Quartz tables | All casehub modules using Quartz |
| [ledger-spi-propagation.md](ledger-spi-propagation.md) | When a LedgerEntryRepository SPI method is added, update all downstream implementations | casehub-work, casehub-qhorus, casehub-engine |
| [spi-default-method-contract-test.md](spi-default-method-contract-test.md) | Verify SPI default method contracts with an anonymous implementation test — compiler error is the RED state | All SPI interfaces using default methods |
| [qhorus-event-content-null.md](qhorus-event-content-null.md) | EVENT message `content` is always null — render telemetry fields instead | All projects reading Qhorus ledger entries |
| [qhorus-human-governance-channel-types.md](qhorus-human-governance-channel-types.md) | Oversight channel must have `allowedTypes=QUERY,COMMAND`; human actors never post EVENT | All projects using Qhorus NormativeChannelLayout |
| [qhorus-actor-type-mapping.md](qhorus-actor-type-mapping.md) | All ActorType values must map to the canonical casehub ledger vocabulary | All casehubio projects assigning ActorType |
| [maven-coordinate-standard.md](maven-coordinate-standard.md) | Maven coordinate standard for all casehubio repos | All casehubio Maven repos |
| [artifact-rename-propagation.md](artifact-rename-propagation.md) | Artifact rename propagation — update all cross-repo consumers before shipping | Any casehubio repo renaming a published artifactId |
| [java-optional-usage.md](java-optional-usage.md) | Use Optional only when absence is the method's primary return contract | All Java code across casehub |
| [quarkus-test-security-http-only.md](quarkus-test-security-http-only.md) | Only add @TestSecurity to @QuarkusTest classes that exercise HTTP endpoints | All modules with @QuarkusTest classes |

---

## Garden References

Generic Quarkus/Java knowledge migrated from casehub conventions to the canonical garden.
These entries are universally applicable — not casehub-specific.
Listed here for discoverability until garden RAG is available.

### CDI / Transactions

| GE-ID | Title | Garden domain |
|---|---|---|
| GE-20260512-66d997 | Panache static methods bypass CDI @Alternative stores — returns empty results silently | jvm |
| GE-20260512-0fe012 | CDI fireAsync() inside @Transactional dispatches immediately — observer can run before commit | jvm |
| GE-20260512-6887c9 | @ObservesAsync + @Transactional on same method is unreliable — delegate to separate bean | jvm |
| GE-20260512-a9ad9f | Raw ExecutorService drops CDI context — @Transactional silently broken on background threads | jvm |
| GE-20260512-6d0c2b | BroadcastProcessor.onNext() throws BackPressureFailure when no subscribers are registered | jvm |

### Quarkus Testing

| GE-ID | Title | Garden domain |
|---|---|---|
| GE-20260512-47f92e | quarkus-junit5 is a relocation stub since Quarkus 3.31 — use quarkus-junit | jvm |
| GE-20260512-b3f32a | @IfBuildProperty/@UnlessBuildProperty evaluated at augmentation only — QuarkusTestProfile has no effect | jvm |
| GE-20260512-e552f7 | @ApplicationScoped bean state persists across @QuarkusTest classes — tests pass in isolation, fail in suite | jvm |
| GE-20260512-50b394 | Use @TestTransaction + unique identifiers to prevent @Scheduled interference in tests | jvm |
| GE-20260512-c246b0 | Test CDI SPI with @Alternative static inner classes — Mockito cannot be injected as CDI beans | jvm |
| GE-20260512-493c90 | @QuarkusTest classes named *IT.java silently report 0 tests — failsafe collects them, not surefire | jvm |
| GE-20260512-c30f52 | @QuarkusIntegrationTest in runtime module causes class loading failures — separate module required | jvm |
| GE-20260513-3c1a03 | @TestSecurity silently ignored on @QuarkusTest classes that never touch HTTP | jvm |
| GE-20260513-4c4205 | Use AtomicInteger call counter in Supplier<String> to distinguish SSE events by content in tests | jvm |

### Database / Schema / Migrations

| GE-ID | Title | Garden domain |
|---|---|---|
| GE-20260512-ea776c | Quarkus named persistence units silently skip schema generation — explicit config per named PU | jvm |
| GE-20260512-a3838e | Transitive hibernate-reactive-panache causes H2 test startup failure — disable reactive datasource | jvm |
| GE-20260512-7720ab | H2-reserved words as column names pass PostgreSQL but fail in H2 test mode | jvm |
| GE-20260512-2c2eff | Non-ANSI SQL types in Flyway migrations pass H2 silently but fail on PostgreSQL at deployment | jvm |
| GE-20260512-67b3b5 | Panache find() alias-prefixed field names return empty results silently — bare field names required | jvm |

### Scheduler / Config

| GE-ID | Title | Garden domain |
|---|---|---|
| GE-20260512-1fa51e | @Scheduled interval without $ prefix silently fires at wrong frequency | jvm |
| GE-20260512-552405 | @ConfigMapping methods without Javadoc cause a compile error — not a runtime warning | jvm |
| GE-20260512-523f68 | Quarkus dev mode hot-reload silently breaks WebSocket endpoint registration | jvm |

### Architecture / Design Techniques

| GE-ID | Title | Garden domain |
|---|---|---|
| GE-20260512-e3e525 | OCC + policyTriggered flag for M-of-N threshold completion — prevents duplicate trigger under READ COMMITTED | jvm |
| GE-20260512-a09bd3 | Enforce blocking/reactive SPI method parity with a reflection test | jvm |

### Tooling

| GE-ID | Title | Garden domain |
|---|---|---|
| GE-20260512-a28ecc | Maven relative paths resolve to wrong worktree when shell cwd changes — use absolute paths | tools |

---

## Casehub Domain Garden Entries

Casehub-specific knowledge moved from `quarkus/` to casehub-* garden domains.
Listed here for discoverability until garden RAG is available.

### casehub-engine/

| GE-ID | Title |
|---|---|
| GE-20260414-10d4da | CNCF Serverless Workflow CallableTaskBuilder.accept(Class) cannot distinguish custom callable names |
| GE-20260414-f4f539 | CaseHubReactor.startCase() no longer calls registerCaseDefinition() — definitions only register at startup |
| GE-20260417-3887be | Reset shared test counter immediately after a blocking startCase() call to minimise async contamination |
| GE-20260417-4a3c22 | Worker lambda receives null for context fields added to inputSchema — keys may not survive event log serialization |
| GE-20260417-d67b22 | Use per-case DB query instead of shared AtomicInteger to isolate @QuarkusTest async worker assertions |
| GE-20260420-18fbd4 | ExpressionEvaluator is a marker-only interface — actual evaluation requires instanceof dispatch to LambdaExpressionEvaluator.test() |
| GE-20260420-4a62d3 | casehub-persistence-memory as Maven test dependency fails for @QuarkusTest — copy sources instead |
| GE-20260421-88296e | persistence-memory Maven profile required for all engine tests without Docker |
| GE-20260428-9311f8 | @ApplicationScoped no-op SPI beans collide with consumer implementations when engine is indexed |
| GE-20260428-9571b8 | Bayesian Beta trust model may store confidence as a field but not use it in the update weight |
| GE-20260428-a67806 | Vert.x event-bus handlers lack @Blocking — JPA consumer calls fail from IO thread |
| GE-20260429-a9bd85 | CaseInstanceRepository.updateStateAndAppendEvent() already appends the EventLog — calling append() first duplicates the write |
| GE-20260512-59a501 | CaseContextImpl.snapshot() returns CaseContextImpl — subclasses lose their type on copy |
| GE-20260512-5bcc7b | Preserve subclass type in CaseContextImpl.snapshot() without accessing private deepCopy |
| GE-20260512-b0eea3 | CaseContextImpl.set(key, null) on an absent key is a no-op — the key is never inserted |

### casehub-work/

| GE-ID | Title |
|---|---|
| GE-20260421-4a9364 | JpaWorkItemStore.scan() with assigneeId also matches candidateUsers LIKE '%actorId%' |
| GE-20260421-9498ff | WorkItemService.delegate() must run strategy BEFORE clearing assigneeId or Hibernate auto-flush corrupts workload counts |
| GE-20260423-3be346 | WorkerCandidate.of(id) creates empty capabilities — WorkBroker filters all candidates when requiredCapabilities is non-null |
| GE-20260427-5d7c67 | quarkus-work (full) brings JpaWorkloadProvider that clashes with any other WorkloadProvider bean |
| GE-20260427-bf4338 | WorkItemStatus.EXPIRED.isTerminal() returns false — EXPIRED is not treated as terminal by quarkus-work |
| GE-20260427-cc77a7 | WorkItemLifecycleEvent.workItem() doesn't exist — access WorkItem via source() cast |
| GE-20260429-cd60ee | Add completeFromSystem()/rejectFromSystem() to WorkItemService to bypass human-actor lifecycle guards |
| GE-20260501-29e3b8 | QuarkusTest: notification rules persist across tests — dynamic WireMock port reuse causes false positives |
| GE-20260502-c77725 | MultiInstanceSpawnService.onThresholdReached defaults to CANCEL — tests completing all children race with coordinator |
| GE-20260511-a28064 | Quarkus Flyway classpath:db/migration scans transitive JARs — casehub-work V1-V21 conflicts with consumer domain migrations |

### casehub-ledger/

| GE-ID | Title |
|---|---|
| GE-20260420-b9259e | LedgerAttestation in quarkus-ledger is plain @Entity — Panache statics cause compile error |
| GE-20260424-6b88a0 | quarkus.ledger.datasource routes LedgerEntityManagerProducer to a named PU — not documented |
| GE-20260427-97650e | CDI ambiguity when adding second implementation of a quarkus-ledger repository interface |
| GE-20260429-2e1c4f | quarkus-ledger sequence_number index is not unique — race yields silent duplicate sequences |

### casehub-qhorus/

| GE-ID | Title |
|---|---|
| GE-20260414-23982b | check_messages excludes EVENT messages by design — tests expecting EVENTs always get fewer results than sent |
| GE-20260501-11ce7f | MessageLedgerEntry.content is null for EVENT entries — LIKE content search silently returns nothing |
| GE-20260501-b12416 | MessageLedgerEntry.sequenceNumber is per-channel, not global — wrong ORDER BY for cross-channel queries |
| GE-20260508-492336 | casehub-qhorus activates quarkus-hibernate-reactive unconditionally — fails with JDBC H2 at startup |
