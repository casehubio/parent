# CaseHub Agentic Harness Protocols

For LLMs building applications on top of CaseHub — domain apps, living labs, any agentic harness
(casehub-aml, casehub-clinical, casehub-devtown, QuarkMind, and any future harness).

**Building the CaseHub platform itself?** Read [FOUNDATION-INDEX.md](FOUNDATION-INDEX.md) instead.

Reconstitute this index: `grep -rl "^scope: application" docs/protocols/*.md`

---

## Protocols

| File | Rule | Applies to |
|------|------|------------|
| [layer-log.md](universal/layer-log.md) | Maintain LAYER-LOG.md as definition of done per harness layer — structured wiring, gotchas, and pattern-to-replicate for each layer | All CaseHub domain applications |
| [case-definition-layers.md](casehub/case-definition-layers.md) | Three-layer case definition architecture — YAML is the runtime format; extend YamlCaseHub; use fluent DSL for tests; LambdaExpressionEvaluator only in tests (not YAML-loaded definitions) | All CaseHub domain applications defining CasePlanModels |
| [casehub-work-illegal-state-exception.md](casehub/casehub-work-illegal-state-exception.md) | Do not throw IllegalStateException in REST-reachable code — casehub-work maps it to HTTP 409 via IllegalStateExceptionMapper | All harnesses using casehub-work |
| [harness-ledger-writer.md](casehub/harness-ledger-writer.md) | Extract a dedicated `@ApplicationScoped` writer bean that owns `sequenceNumber` computation when more than one service writes entries of the same `LedgerEntry` subtype for the same subject | Harnesses with multi-service ledger writes |
| *(pending #18)* | Hexagonal module placement — `api/` is JPA-free pure domain; `app/` owns use-case orchestration | All CaseHub domain applications |
| *(pending #19)* | casehub-work Hibernate scan packages — include both `runtime.model` and `runtime.filter` | All harnesses using casehub-work |
| *(pending)* | Layered adoption approach — one foundation module at a time; each layer independently runnable with a single HTTP call | All CaseHub domain applications |
| *(pending)* | Production-first — do not design or architect for the tutorial; the tutorial documents what you built | All CaseHub domain applications |

---

## Garden References — CaseHub-Specific

Gotchas and techniques discovered while building on CaseHub foundation modules.
For generic Quarkus/Java entries (CDI, testing, migrations), see [FOUNDATION-INDEX.md §Garden](FOUNDATION-INDEX.md).

### casehub-engine

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

### casehub-work

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

### casehub-ledger

| GE-ID | Title |
|---|---|
| GE-20260420-b9259e | LedgerAttestation in quarkus-ledger is plain @Entity — Panache statics cause compile error |
| GE-20260424-6b88a0 | quarkus.ledger.datasource routes LedgerEntityManagerProducer to a named PU — not documented |
| GE-20260427-97650e | CDI ambiguity when adding second implementation of a quarkus-ledger repository interface |
| GE-20260429-2e1c4f | quarkus-ledger sequence_number index is not unique — race yields silent duplicate sequences |

### casehub-qhorus

| GE-ID | Title |
|---|---|
| GE-20260414-23982b | check_messages excludes EVENT messages by design — tests expecting EVENTs always get fewer results than sent |
| GE-20260501-11ce7f | MessageLedgerEntry.content is null for EVENT entries — LIKE content search silently returns nothing |
| GE-20260501-b12416 | MessageLedgerEntry.sequenceNumber is per-channel, not global — wrong ORDER BY for cross-channel queries |
| GE-20260508-492336 | casehub-qhorus activates quarkus-hibernate-reactive unconditionally — fails with JDBC H2 at startup |

### AML-specific (Layer 2 — casehub-work wiring)

| GE-ID | Title |
|---|---|
| GE-20260513-74dc72 | FilterRule scan package — casehub-work Hibernate scan requires io.casehub.work.runtime.filter alongside runtime.model |
| GE-20260513-4f26a7 | @DefaultBean layer displacement — Layer N service with @DefaultBean is displaced by Layer N+1 without @DefaultBean |
