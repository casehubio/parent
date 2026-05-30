---
id: PP-20260530-d4d294
title: "All LedgerEntryEnricher implementations must declare @Priority"
type: rule
scope: repo
applies_to: "casehub-ledger — any class implementing LedgerEntryEnricher"
severity: important
refs:
  - runtime/src/main/java/io/casehub/ledger/runtime/service/LedgerEntryEnricher.java
  - runtime/src/main/java/io/casehub/ledger/runtime/service/LedgerEnricherPipeline.java
violation_hint: "An enricher without @Priority sorts at Integer.MAX_VALUE — after all numbered enrichers. If ActorIdentityValidationEnricher runs before AgentSignatureEnricher, it reads a null agentPublicKey and records KEY_MISMATCH instead of VALID."
created: 2026-05-30
---

Every `LedgerEntryEnricher` implementation must carry `@jakarta.annotation.Priority`. `LedgerEnricherPipeline` sorts enrichers using `InjectableBean.getPriority()` (Arc CDI metadata, not reflection — CDI proxies return null from `getAnnotation()`). Without an explicit `@Priority`, an enricher sorts at `Integer.MAX_VALUE` and runs after all others; enrichers that produce data later-enrichers depend on (e.g. `AgentSignatureEnricher` @20 must precede `ActorIdentityValidationEnricher` @50) will silently receive null fields and produce wrong validation results. Assigned values: TraceIdEnricher=10, AgentSignatureEnricher=20, ProvenanceCaptureEnricher=30, ActorDIDEnricher=40, ActorIdentityValidationEnricher=50.
