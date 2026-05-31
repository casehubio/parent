---
id: PP-20260531-15237d
title: "Per-actorId identity caches in casehub-ledger must observe AgentKeyRotatedEvent for invalidation"
type: rule
scope: repo
applies_to: "casehub-ledger — any CDI bean or AbstractCachingIdentityProvider subclass that caches identity-related data keyed by actorId (DID, binding status, SCIM resource, credential validation result)"
severity: important
refs:
  - runtime/src/main/java/io/casehub/ledger/runtime/service/AgentKeyRotatedEvent.java
  - runtime/src/main/java/io/casehub/ledger/runtime/service/identity/ActorIdentityValidationEnricher.java
  - runtime/src/main/java/io/casehub/ledger/runtime/service/identity/ScimActorDIDProvider.java
violation_hint: "A new ActorDIDProvider or similar cache is added without an @Observes AgentKeyRotatedEvent method. After key rotation, stale identity bindings remain active until TTL expiry — new entries signed with the old key may be incorrectly validated as VALID or UNSIGNED instead of triggering re-validation."
created: 2026-05-31
---

Any cache in casehub-ledger that stores per-actorId identity data — DID URIs, binding status results, SCIM agent resources, or credential validation outcomes — must invalidate its cache entry for an actor when that actor's key is rotated. Implement this by observing `AgentKeyRotatedEvent` with `@Observes` and calling `invalidate(event.actorId())`. `AgentKeyRotatedEvent` is fired by `KeyRotationService.recordRotation()` after the rotation entry is persisted. For implementations based on `AbstractCachingIdentityProvider`, the inherited `invalidate(key)` method is sufficient. Reactive services that fire via `fireAsync()` deliver the event on a separate thread — use `@ObservesAsync` if the cache implementation is reactive.
