# casehub-platform-identity — Platform Deep Dive

**GitHub:** [casehubio/platform](https://github.com/casehubio/platform) (submodule: `identity/`)
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Platform-wide DID resolution, Verifiable Credential validation, and SCIM2-based agent identity
lookup. These capabilities are platform infrastructure — not ledger-specific — so they belong
in `casehub-platform` alongside SCIM group membership and OIDC identity, not in the audit
extension that first needed them.

`casehub-ledger` is a consumer of these SPIs, not their owner. Any Quarkus application that
needs to resolve actor DIDs, validate JWTs or W3C VCs, or look up agent identity attributes
from a SCIM2 directory can add `casehub-platform-identity` as a compile dependency and
immediately get defaults that can be displaced by activating the built-in alternatives.

---

## Modules

| Directory | Artifact ID | Purpose |
|-----------|-------------|---------|
| `identity/api/` | `casehub-platform-identity-api` | Pure-Java SPIs and model types — no JPA, no Quarkus, no framework deps |
| `identity/` | `casehub-platform-identity` | `@DefaultBean` no-ops + built-in alternatives: `KeyDIDResolver`, `WebDIDResolver`, `ConfiguredActorDIDProvider`, `ScimActorDIDProvider`, `AbstractCachingIdentityProvider` |

---

## Key Abstractions

### SPIs (in `casehub-platform-identity-api`)

| SPI | Default | Purpose |
|-----|---------|---------|
| `ActorDIDProvider` | `NoOpActorDIDProvider` — always returns `Optional.empty()` | Resolve an `actorId` string to a DID URI. Called at write time by `ActorDIDEnricher` (in ledger) to populate `LedgerEntry.actorDid`. |
| `DIDResolver` | `NoOpDIDResolver` — always returns `Optional.empty()` | Resolve a DID URI to a `DIDDocument`. Used by `ActorIdentityValidationEnricher` (in ledger) to verify the public key claim. |
| `AgentCredentialValidator` | `NoOpCredentialValidator` — always returns `VALID` | Validate a W3C Verifiable Credential payload. Called in the identity binding validation pipeline. |

### Model Types (in `casehub-platform-identity-api`)

| Type | Kind | Description |
|------|------|-------------|
| `DIDDocument` | record | Resolved DID document — `id`, `verificationMethods`, `assertionMethods`, `authentication` |
| `VerificationMethod` | record | Single entry in a DID document — `id`, `type`, `controller`, `publicKeyMultibase` |
| `IdentityVerificationResult` | enum | `VALID \| UNVERIFIABLE \| UNSIGNED \| DID_UNRESOLVABLE \| IDENTITY_MISMATCH \| KEY_MISMATCH` |
| `CredentialValidationResult` | enum | `VALID \| EXPIRED \| INVALID_SIGNATURE \| ISSUER_UNKNOWN \| NOT_FOUND` |
| `IdentityBindingStatus` | enum | `VALID \| UNSIGNED \| DID_UNRESOLVABLE \| IDENTITY_MISMATCH \| KEY_MISMATCH \| CREDENTIAL_EXPIRED \| CREDENTIAL_INVALID` |
| `AgentIdentityValidatedEvent` | CDI event record | Fired (async) when the identity binding pipeline returns `VALID` |
| `AgentIdentityViolationEvent` | CDI event record | Fired (async) when the identity binding pipeline returns a non-VALID result |

### Built-in Alternatives (in `casehub-platform-identity`)

| Class | Activation | Description |
|-------|-----------|-------------|
| `NoOpActorDIDProvider` | `@DefaultBean` — always active | Returns `Optional.empty()` for every actorId |
| `NoOpDIDResolver` | `@DefaultBean` — always active | Returns `Optional.empty()` for every DID URI |
| `NoOpCredentialValidator` | `@DefaultBean` — always active | Returns `CredentialValidationResult.VALID` for every credential |
| `CompositeActorDIDProvider` | `@ApplicationScoped` — automatically active | Iterates `@ActorDIDSource` providers by `@Priority` (platform#128). First non-empty result wins. Enables multi-source resolution (config fallback to SCIM). |
| `ConfiguredActorDIDProvider` | `@ActorDIDSource @Alternative` — activate via `quarkus.arc.selected-alternatives` | Static `actorId → DID` mapping from config (`casehub.identity.dids.*`). No HTTP; suitable for testing and single-tenant deployments. |
| `KeyDIDResolver` | `@Alternative` — activate via `quarkus.arc.selected-alternatives` | Resolves `did:key` URIs via multicodec dispatch (platform#130). Supports Ed25519 (0xed) and P-256 (0x1200) with varint decoding. Populates `alsoKnownAs` from actorId. No HTTP calls. |
| `WebDIDResolver` | `@Alternative` — activate via `quarkus.arc.selected-alternatives` | Resolves `did:web` URIs by fetching `https://<hostname>/.well-known/did.json`. SSRF protection: configurable allowlist/blocklist, private-range blocking enabled by default. |
| `ScimActorDIDProvider` | `@ActorDIDSource @Alternative @ApplicationScoped` — activate via `quarkus.arc.selected-alternatives` | Resolves `actorId → DID` via SCIM2 `Agent` endpoint (`externalId` = `actorId`). TTL cache. Invalidates on `AgentKeyRotatedEvent`. Config prefix: `casehub.identity.scim.*`. Lazy HTTPS validation (platform#132). |

`AbstractCachingIdentityProvider` is a base class for building TTL-capable generic caches
with atomic eviction and external-driven `put()` invalidation. `ScimActorDIDProvider` extends it.

---

## Configuration

| Prefix | Purpose |
|--------|---------|
| `casehub.identity.dids.*` | Static actorId → DID mapping for `ConfiguredActorDIDProvider` |
| `casehub.identity.scim.*` | SCIM2 endpoint + auth for `ScimActorDIDProvider` |
| `casehub.identity.web-resolver-*` | SSRF allowlist/blocklist for `WebDIDResolver` |

Note: `casehub.ledger.agent-identity.validation-mode` (PERMISSIVE / ENFORCE) is ledger-specific
config and remains in `casehub-ledger`. Only the resolution and lookup config moved here.

---

## Package Structure

```
io.casehub.platform.api.identity   (casehub-platform-identity-api)
  ActorDIDProvider                 — SPI
  DIDResolver                      — SPI
  AgentCredentialValidator         — SPI
  DIDDocument                      — record
  VerificationMethod               — record
  IdentityVerificationResult       — enum
  CredentialValidationResult       — enum
  IdentityBindingStatus            — enum
  AgentIdentityValidatedEvent      — CDI event record
  AgentIdentityViolationEvent      — CDI event record

io.casehub.platform.identity       (casehub-platform-identity)
  AbstractCachingIdentityProvider  — generic TTL cache base
  NoOpActorDIDProvider             — @DefaultBean
  NoOpDIDResolver                  — @DefaultBean
  NoOpCredentialValidator          — @DefaultBean
  CompositeActorDIDProvider        — @ApplicationScoped (iterates @ActorDIDSource by @Priority)
  ConfiguredActorDIDProvider       — @ActorDIDSource @Alternative (config-based)
  KeyDIDResolver                   — @Alternative (did:key, multicodec dispatch, Ed25519/P-256)
  MulticodecKeyType                — enum: Ed25519/P-256 SPKI encoding
  WebDIDResolver                   — @Alternative (did:web, SSRF protection)
  ScimActorDIDProvider             — @ActorDIDSource @Alternative @ApplicationScoped (SCIM2 lookup)
  ScimAgentResource                — record: cached SCIM2 agent lookup result
```

---

## Maven Coordinates

| Element | Value |
|---------|-------|
| groupId | `io.casehub` |
| API artifactId | `casehub-platform-identity-api` |
| Runtime artifactId | `casehub-platform-identity` |
| Version | `0.2-SNAPSHOT` |
| Config prefix | `casehub.identity` |

---

## Depends On

Nothing in the casehubio ecosystem. Zero external framework dependencies in the `api/` module.
The `identity/` runtime module depends on Quarkus CDI + SmallRye Config only.

## Depended On By

| Repo | Module | How |
|------|--------|-----|
| `casehub-ledger` | `runtime` | `ActorDIDProvider`, `DIDResolver`, `AgentCredentialValidator` SPIs consumed by `ActorDIDEnricher` and `ActorIdentityValidationEnricher`; CDI event records used in identity pipeline |

---

## What This Module Explicitly Does NOT Do

- Persist identity bindings (that is `casehub-ledger` — `ActorIdentityBindingEntry` entity + `ActorIdentityBindingRepository`)
- Enforce validation mode (PERMISSIVE / ENFORCE lives in `casehub-ledger` — `LedgerIdentityEnforcementListener`)
- Enrich ledger entries at write time (that is `casehub-ledger` — `ActorDIDEnricher` + `ActorIdentityValidationEnricher`)
- Fire `AgentKeyRotatedEvent` (that is `casehub-ledger` — `KeyRotationService`)

---

## Consumer Pattern

To activate DID resolution and agent identity lookup in any Quarkus application:

```xml
<!-- Add to pom.xml -->
<dependency>
  <groupId>io.casehub</groupId>
  <artifactId>casehub-platform-identity</artifactId>
</dependency>
```

Then select the alternative that fits the deployment:

```properties
# did:key resolution (no HTTP, cryptographic)
quarkus.arc.selected-alternatives=io.casehub.platform.identity.KeyDIDResolver

# did:web resolution (HTTPS fetch, SSRF-protected)
quarkus.arc.selected-alternatives=io.casehub.platform.identity.WebDIDResolver

# SCIM2 agent directory lookup
quarkus.arc.selected-alternatives=io.casehub.platform.identity.ScimActorDIDProvider
casehub.identity.scim.endpoint=https://scim.example.com/v2
casehub.identity.scim.token=<bearer-token>

# Static mapping for test or single-tenant
quarkus.arc.selected-alternatives=io.casehub.platform.identity.ConfiguredActorDIDProvider
casehub.identity.dids."claude:analyst@v1"=did:key:z6Mk...
```

Multiple alternatives can be selected simultaneously (e.g. `KeyDIDResolver` + `ScimActorDIDProvider`).

---

## See Also

- [`docs/repos/casehub-ledger.md`](casehub-ledger.md) — the primary consumer; owns enrichers, binding persistence, enforcement
- [`docs/repos/casehub-platform.md`](casehub-platform.md) — sibling modules (OIDC, SCIM group membership, memory adapters)
- [`integration/scim2-agent-identity.md`](../integration/scim2-agent-identity.md) — SCIM2 `Agent` endpoint schema and filter protocol
- [capability-ownership.md](../platform/capability-ownership.md) — DID/VC resolution entry
